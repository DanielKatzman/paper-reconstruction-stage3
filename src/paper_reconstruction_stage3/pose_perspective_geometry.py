"""Bounded multi-start similarity and regularized projective contour refinement."""
import numpy as np
from .alignment import apply_transform,fit_transforms
from .pose_boundary_evidence import correspondences,transformed
from .projective import fit_homography,warp_check,grid


def blocks(n,count):return np.minimum(np.arange(n)*count//n,count-1)


def distances(first,second,matrix):
    a=np.asarray(first['points_xy_crop']);an=np.asarray(first['inward_normal_xy_crop'])
    b,bn,_=transformed(second,matrix)
    da,ja,ua,pa=correspondences(a,an,b,bn);db,jb,ub,pb=correspondences(b,bn,a,an)
    return da,db,pa,pb,ja,jb


def validate_fixed(first,second,matrix,fixed,policy):
    da,db,_,_,_,_=distances(first,second,matrix);scores=[];support=[];groups=[]
    for d,use in zip((da,db),fixed):
        scores.extend(np.exp(-d[use]/4.));support.extend(d[use]<=policy['refinement_distance_px'])
        identity=blocks(len(d),policy['validation_blocks'])
        groups.extend(float(np.exp(-d[use&(identity==i)]/4.).mean()) for i in range(policy['validation_blocks']) if np.any(use&(identity==i)))
    return {'score':float(np.mean(scores)) if scores else 0.,'support_fraction':float(np.mean(support)) if support else 0.,
        'block_scores':groups,'samples':[int(x.sum()) for x in fixed]}


def refine(first,second,pose,initial,family,base,policy,source_shape,target_shape):
    origin=np.asarray(pose['alignment']['transform'],float);current=np.asarray(initial,float).copy()
    da,db,_,_,_,_=distances(first,second,origin)
    # Alternate contiguous blocks fit/validate. Fixed validation samples cannot
    # disappear when a fitted warp loses support. This is a development check,
    # not an independent statistical holdout or an identifiability certificate.
    fixed=[(blocks(len(d),policy['validation_blocks'])%2==(1-side))&(d<=policy['refinement_distance_px']) for side,d in enumerate((da,db))]
    before=validate_fixed(first,second,origin,fixed,policy);best=before;accepted=0;fit_details={};rejections=[]
    if min(before['samples'])<policy['minimum_validation_samples']:
        return origin,{'accepted_iterations':0,'reason':'insufficient_fixed_validation','before':before,'after':before}
    native_a=np.asarray(first['points_xy_crop']);native_b=np.asarray(second['points_xy_crop'])
    points=grid(source_shape);diagonal=float(np.hypot(*source_shape))
    bound=min(policy['maximum_probe_displacement_px'],max(policy['minimum_refinement_displacement_px'],policy['maximum_probe_displacement_fraction']*diagonal))
    for _ in range(policy['refinement_iterations']):
        da,db,pa,pb,ja,jb=distances(first,second,current)
        ia=(blocks(len(da),policy['validation_blocks'])%2==0)&(da<=policy['refinement_distance_px'])
        ib=(blocks(len(db),policy['validation_blocks'])%2==1)&(db<=policy['refinement_distance_px'])
        ta=blocks(len(da),policy['validation_blocks'])%2==0;tb=blocks(len(db),policy['validation_blocks'])%2==1
        ia &= tb[ja]&tb[ja+1];ib &= ta[jb]&ta[jb+1]
        # Inverse projection preserves the correct native coordinate on a
        # projectively mapped segment; linear native interpolation does not.
        x=np.concatenate((native_a[ia],pb[ib]));y=np.concatenate((apply_transform(pa[ia],np.linalg.inv(current)),native_b[ib]))
        errors=np.concatenate((da[ia],db[ib]))
        if len(x)<policy['minimum_fit_pairs']:rejections.append('insufficient_fit_pairs');break
        keep=errors<=max(float(np.quantile(errors,policy['robust_keep_fraction'])),1e-8);x,y=x[keep],y[keep]
        if len(x)<policy['minimum_fit_pairs'] or min(np.linalg.norm(np.ptp(x,axis=0)),np.linalg.norm(np.ptp(y,axis=0)))<policy['minimum_fit_length_px']:
            rejections.append('short_fit_support');break
        if family=='similarity':
            candidate=fit_transforms(x[None],y[None],similarity=True,scale_bounds=(base['minimum_scale'],base['maximum_scale']))[0][0]
            fit_details={'reason':'fitted','fit_pairs':len(x)}
        else:
            candidate,fit_details=fit_homography(x,y,current,policy)
            if candidate is None:rejections.append(fit_details['reason']);break
        fitted=candidate;accepted_step=None;reason='fixed_validation_not_improved'
        for fraction in policy['refinement_step_fractions']:
            candidate=current+fraction*(fitted-current)
            check=warp_check(candidate,source_shape,target_shape,policy)
            if not check['valid']:reason=check['reason'];continue
            if family=='similarity':
                scale=float(np.sqrt(np.linalg.det(candidate[:2,:2])))
                if not base['minimum_scale']-1e-10<=scale<=base['maximum_scale']+1e-10:reason='similarity_scale_out_of_bounds';continue
            displacement=float(np.max(np.linalg.norm(apply_transform(points,candidate)-apply_transform(points,origin),axis=1)))
            if displacement>bound:reason='whole_crop_displacement';continue
            value=validate_fixed(first,second,candidate,fixed,policy)
            if value['score']<=best['score']+policy['validation_score_improvement'] or value['support_fraction']<policy['validation_support_ratio']*before['support_fraction']:
                reason='fixed_validation_not_improved';continue
            if any(a<b-policy['validation_block_score_slack'] for a,b in zip(value['block_scores'],before['block_scores'])):
                reason='validation_block_regressed';continue
            accepted_step=(candidate,value);fit_details['step_fraction']=fraction;break
        if accepted_step is None:rejections.append(reason);break
        candidate,value=accepted_step
        current=candidate;best=value;accepted+=1
    return current,{'accepted_iterations':accepted,'before':before,'after':best,'fit':fit_details,
        'rejections':rejections,'maximum_probe_displacement_px':float(np.max(np.linalg.norm(apply_transform(points,current)-apply_transform(points,origin),axis=1))),
        'displacement_bound_px':bound,'scope':'Observable nearest normal-compatible contour projections; alternate contiguous fit/validation blocks, fixed validation support, bounded full-crop warp. Repeated use of validation blocks is not an independent test.'}
