def mirror_shape(blendshape_name=""):
    
    source = pm.ls(sl=True)[0]
    target = pm.ls(sl=True)[1]
    
    dup = pm.duplicate(target)[0]
    
    bs = pm.blendShape(target)[0]
    pm.blendShape(bs, edit=True, target=(target.getShape(), 0, dup, 1.0))
    pm.setAttr(bs+"."+dup, 1)
    
    for cv in source.getShape().cv: 
        u = cv.indices()[0][0]
        v = cv.indices()[0][1]
        tran = pm.xform(cv, worldSpace=True, translation=True, q=True)
        pm.move(dup.getShape().cv[1-u][v], [tran[0]*-1, tran[1], tran[2]])
    
    pm.delete(dup)