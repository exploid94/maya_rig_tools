import pymel.core as pm
from mgear.core import transform, primitive, node

def connectSpace(refArray, cns_obj, ctl=None, pre_self_ctl=None, post_self_ctl=None, create_null=True, space_type="parent", space_attr_type="enum", space_attr_name="spaceSwitch"):
        """Connect the cns_obj to a multiple object using parentConstraint.

        Args:
            refArray (list of dagNode): List of driver objects
            cns_obj (dagNode): The driven object.
            ctl (dagNode): Control to put the space switch on
            self_ctl (list of dagNode): List of driver objects within the current component
            create_null (bool): Used to create a groupd under the ref object that the cns_obj will be constrained to
            space_type (str): Determines which type of constraints to make
        """
        if refArray:

            # convert lists of objs in ref to be appended to the ref list instead
            new_ref = []
            if pre_self_ctl:
                for i in pre_self_ctl:
                    new_ref.append(i)
            x = 0
            if isinstance(refArray, list):
                for i in refArray:
                    if isinstance(i, list):
                        for item in i:
                            new_ref.append(item)
                    else:
                        new_ref.append(i)
            else:
                new_ref.append(refArray)
            
            if post_self_ctl:
                for i in post_self_ctl:
                    new_ref.append(i)
            
            nul_ref = []

            # need to add the parent node as a target for blending when total value is below 1, otherwise it will snap
            new_ref.append(cns_obj.getParent())

            if create_null:
                if isinstance(new_ref, list):
                    for i in new_ref:
                        t = transform.getTransform(cns_obj)
                        tmp_name = cns_obj+"_follow_"+i+"_spc"
                        zero_name = cns_obj+"_follow_"+i+"_zero"
                        if t.scale != transform.getTransform(i).scale:
                            zero = primitive.addTransform(i, zero_name, t)
                            nul = primitive.addTransform(zero, tmp_name, t)
                        else:
                            nul = primitive.addTransform(i, tmp_name, t)
                        nul_ref.append(nul)

                        # need to reparent the transform so the point and orient doesn't orbit
                        if space_type == "point_and_orient":
                            pm.parent(nul, cns_obj.getParent())
                            pm.pointConstraint(i, nul, mo=True)
                            pm.orientConstraint(i, nul, mo=True)
                        elif space_type == "point":
                            pm.parent(nul, cns_obj.getParent())
                            pm.pointConstraint(i, nul, mo=True)

                else:
                    t = transform.getTransform(cns_obj)
                    tmp_name = cns_obj+"_follow_"+new_ref+"_spc"
                    nul = primitive.addTransform(new_ref, tmp_name, t)
                    nul_ref.append(nul)

                    # need to reparent the transform so the point and orient doesn't orbit
                    if space_type == "point_and_orient":
                        pm.parent(nul, cns_obj.getParent())
                        pm.pointConstraint(new_ref, nul, mo=True)
                        pm.orientConstraint(new_ref, nul, mo=True)
                    elif space_type == "point":
                        pm.parent(nul, cns_obj.getParent())
                        pm.pointConstraint(new_ref, nul, mo=True)

                new_ref = nul_ref
        

            # determing the type of constraints to make, fall back to parent if flag string is incorrect
            # point will not parent under space, instead it will point constrain to it with offset
            # orbit will parent under space so it orbits the parent space
            if space_type == "parent":
                parent_node = pm.parentConstraint(new_ref, cns_obj, maintainOffset=True)
                point_node = None
                orient_node = None
                orbit_node = None
            elif space_type == "point_and_orient":
                parent_node = None
                point_node = pm.pointConstraint(new_ref, cns_obj, maintainOffset=True)
                orient_node = pm.orientConstraint(new_ref, cns_obj, maintainOffset=True)
                orbit_node = None
            elif space_type == "point":
                parent_node = None
                point_node = pm.pointConstraint(new_ref, cns_obj, maintainOffset=True)
                orient_node = None
                orbit_node = None
            elif space_type == "orient":
                parent_node = None
                point_node = None
                orient_node = pm.orientConstraint(new_ref, cns_obj, maintainOffset=True)
                orbit_node = None
            elif space_type == "orbit_and_orient":
                parent_node = None
                point_node = None
                orient_node = pm.orientConstraint(new_ref, cns_obj, maintainOffset=True)
                orbit_node = pm.pointConstraint(new_ref, cns_obj, maintainOffset=True)
            elif space_type == "orbit":
                parent_node = None
                point_node = None
                orient_node = None
                orbit_node = pm.pointConstraint(new_ref, cns_obj, maintainOffset=True)
            else:
                parent_node = pm.parentConstraint(new_ref, cns_obj, maintainOffset=True)
                point_node = None
                orient_node = None
                orbit_node = None

            scale_node = pm.scaleConstraint(new_ref, cns_obj, maintainOffset=True)

            
            # need to reparent 

            # constrain to controls within the current module
            if ctl:
                # get the constraint tagets
                if parent_node:
                    if space_attr_type == "enum":
                        parent_con_targets = pm.parentConstraint(parent_node, query=True, weightAliasList=True)
                    elif space_attr_type == "float":
                        parent_con_targets = pm.parentConstraint(parent_node, query=True, weightAliasList=True)[:-1]
                    parent_cns_target = pm.parentConstraint(parent_node, query=True, weightAliasList=True)[-1]
                else:
                    parent_con_targets = None
                    parent_cns_target = None
                if point_node:
                    if space_attr_type == "enum":
                        point_con_targets = pm.pointConstraint(point_node, query=True, weightAliasList=True)
                    if space_attr_type == "float":
                        point_con_targets = pm.pointConstraint(point_node, query=True, weightAliasList=True)[:-1]
                    point_cns_target = pm.pointConstraint(point_node, query=True, weightAliasList=True)[-1]
                else:
                    point_con_targets = None
                    point_cns_target = None
                if orient_node:
                    if space_attr_type == "enum":
                        orient_con_targets = pm.orientConstraint(orient_node, query=True, weightAliasList=True)
                    if space_attr_type == "float":
                        orient_con_targets = pm.orientConstraint(orient_node, query=True, weightAliasList=True)[:-1]
                    orient_cns_target = pm.orientConstraint(orient_node, query=True, weightAliasList=True)[-1]
                else:
                    orient_con_targets = None
                    orient_cns_target = None
                if orbit_node:
                    if space_attr_type == "enum":
                        orbit_con_targets = pm.pointConstraint(orbit_node, query=True, weightAliasList=True)
                    if space_attr_type == "float":
                        orbit_con_targets = pm.pointConstraint(orbit_node, query=True, weightAliasList=True)[:-1]
                    orbit_cns_target = pm.pointConstraint(orbit_node, query=True, weightAliasList=True)[-1]
                else:
                    orbit_con_targets = None
                    orbit_cns_target = None

                if space_attr_type == "enum":
                    scale_con_targets = pm.scaleConstraint(scale_node, query=True, weightAliasList=True)
                if space_attr_type == "float":
                    scale_con_targets = pm.scaleConstraint(scale_node, query=True, weightAliasList=True)[:-1]
                scale_cns_target = pm.scaleConstraint(scale_node, query=True, weightAliasList=True)[-1]
                
                # create an enum list for the space switch attributes
                parent_enum_list = []
                point_enum_list = []
                orient_enum_list = []
                orbit_enum_list = []

                parent_nice_enum_list = []
                point_nice_enum_list = []
                orient_nice_enum_list = []
                orbit_nice_enum_list = []

                # append to the enum list based on targets
                if parent_node:
                    for x in parent_con_targets:
                        name = str(x).split(".")[1]
                        if space_attr_type == "enum":
                            name = str(name[:len(str(name))-2])+":"
                        elif space_attr_type == "float":
                            name = str(name[:len(str(name))-2])
                        if "_follow_" in name:
                            name = name.split("_follow_")[1]
                            name = name.replace("_spc", "")
                        parent_enum_list.append(name)
                        parent_nice_enum_list.append(name.split("_")[0].replace("Sub", ""))
                if point_node:
                    for x in point_con_targets:
                        name = str(x).split(".")[1]
                        if space_attr_type == "enum":
                            name = str(name[:len(str(name))-2])+":"
                        elif space_attr_type == "float":
                            name = str(name[:len(str(name))-2])
                        if "_follow_" in name:
                            name = name.split("_follow_")[1]
                            name = name.replace("_spc", "")
                        point_enum_list.append(name)
                        point_nice_enum_list.append(name.split("_")[0].replace("Sub", ""))
                if orient_node:
                    for x in orient_con_targets:
                        name = str(x).split(".")[1]
                        if space_attr_type == "enum":
                            name = str(name[:len(str(name))-2])+":"
                        elif space_attr_type == "float":
                            name = str(name[:len(str(name))-2])
                        if "_follow_" in name:
                            name = name.split("_follow_")[1]
                            name = name.replace("_spc", "")
                        orient_enum_list.append(name)
                        orient_nice_enum_list.append(name.split("_")[0].replace("Sub", ""))
                if orbit_node:
                    for x in orbit_con_targets:
                        name = str(x).split(".")[1]
                        if space_attr_type == "enum":
                            name = str(name[:len(str(name))-2])+":"
                        elif space_attr_type == "float":
                            name = str(name[:len(str(name))-2])
                        if "_follow_" in name:
                            name = name.split("_follow_")[1]
                            name = name.replace("_spc", "")
                        orbit_enum_list.append(name)
                        orbit_nice_enum_list.append(name.split("_")[0].replace("Sub", ""))

                # add space switch attributes on control specified
                if space_attr_type == "enum":
                    if parent_node:
                        pm.addAttr(ctl, longName=space_attr_name+"Parent", k=True, at="enum", enumName=parent_nice_enum_list)
                    if point_node:
                        pm.addAttr(ctl, longName=space_attr_name+"Point", k=True, at="enum", enumName=point_nice_enum_list)
                    if orbit_node:
                        pm.addAttr(ctl, longName=space_attr_name+"Orbit", k=True, at="enum", enumName=orbit_nice_enum_list)
                    if orient_node:
                        pm.addAttr(ctl, longName=space_attr_name+"Orient", k=True, at="enum", enumName=orient_nice_enum_list)
                
                elif space_attr_type == "float":
                    if parent_node:
                        parent_attr_list = []
                        pm.addAttr(ctl, longName=space_attr_name+"Parent", k=True, at="enum", enumName=["----------"])
                        for x, item in enumerate(parent_enum_list):
                            if x == 0:
                                dv = 1
                            else:
                                dv = 0
                            pm.addAttr(ctl, longName=item+"_parent", niceName=parent_nice_enum_list[x], k=True, at="float", min=0, max=1, dv=dv)
                            parent_attr_list.append(ctl+"."+item+"_parent")
                    if point_node:
                        point_attr_list = []
                        pm.addAttr(ctl, longName=space_attr_name+"Point", k=True, at="enum", enumName=["----------"])
                        for x, item in enumerate(point_enum_list):
                            if x == 0:
                                dv = 1
                            else:
                                dv = 0
                            pm.addAttr(ctl, longName=item+"_point", niceName=point_nice_enum_list[x], k=True, at="float", min=0, max=1, dv=dv)
                            point_attr_list.append(ctl+"."+item+"_point")
                    if orbit_node:
                        orbit_attr_list = []
                        pm.addAttr(ctl, longName=space_attr_name+"Orbit", k=True, at="enum", enumName=["----------"])
                        for x, item in enumerate(orbit_enum_list):
                            if x == 0:
                                dv = 1
                            else:
                                dv = 0
                            pm.addAttr(ctl, longName=item+"_orbit", niceName=orbit_nice_enum_list[x], k=True, at="float", min=0, max=1, dv=dv)
                            orbit_attr_list.append(ctl+"."+item+"_orbit")
                    if orient_node:
                        orient_attr_list = []
                        pm.addAttr(ctl, longName=space_attr_name+"Orient", k=True, at="enum", enumName=["----------"])
                        for x, item in enumerate(orient_enum_list):
                            if x == 0:
                                dv = 1
                            else:
                                dv = 0
                            pm.addAttr(ctl, longName=item+"_orient", niceName=orient_nice_enum_list[x], k=True, at="float", min=0, max=1, dv=dv)
                            orient_attr_list.append(ctl+"."+item+"_orient")


                # create a condition node for the parent constraint
                if parent_node:
                    for x, attr in enumerate(parent_con_targets):
                        node_name = pm.createNode("condition", name="parentConstraint_condition")
                        if space_attr_type == "enum":
                            pm.connectAttr(ctl.spaceSwitchParent, node_name + ".firstTerm")
                            pm.setAttr(node_name + ".colorIfTrueR", 1)
                            pm.setAttr(node_name + ".secondTerm", x)
                            pm.setAttr(node_name + ".operation", 0)
                        elif space_attr_type == "float":
                            pm.connectAttr(parent_attr_list[x], node_name + ".firstTerm")
                            pm.connectAttr(parent_attr_list[x], node_name + ".colorIfTrueR")
                            pm.setAttr(node_name + ".secondTerm", 1)
                            pm.setAttr(node_name + ".operation", 5)
                        pm.setAttr(node_name + ".colorIfFalseR", 0)
                        pm.connectAttr(node_name + ".outColorR", attr)
                    if space_attr_type == "enum":
                        pass
                    elif space_attr_type == "float":
                        # create setup for the cns parent target
                        add = node.createPlusMinusAverage1D(parent_attr_list)
                        remap = node.createRemapValueNode(add.output1D, 0, 1, 0, 1)
                        node.createReverseNode(remap.outValue, parent_cns_target)

                # create a condition node for the point constraint
                if point_node:
                    for x, attr in enumerate(point_con_targets):
                        node_name = pm.createNode("condition", name="pointConstraint_condition")
                        if space_attr_type == "enum":
                            pm.connectAttr(ctl.spaceSwitchPoint, node_name + ".firstTerm")
                            pm.setAttr(node_name + ".colorIfTrueR", 1)
                            pm.setAttr(node_name + ".secondTerm", x)
                            pm.setAttr(node_name + ".operation", 0)
                        elif space_attr_type == "float":
                            pm.connectAttr(point_attr_list[x], node_name + ".firstTerm")
                            pm.connectAttr(point_attr_list[x], node_name + ".colorIfTrueR")
                            pm.setAttr(node_name + ".secondTerm", 1)
                            pm.setAttr(node_name + ".operation", 5)
                        pm.setAttr(node_name + ".colorIfFalseR", 0)
                        pm.connectAttr(node_name + ".outColorR", attr)
                    if space_attr_type == "enum":
                        pass
                    elif space_attr_type == "float":
                        # create setup for the cns parent target
                        add = node.createPlusMinusAverage1D(point_attr_list)
                        remap = node.createRemapValueNode(add.output1D, 0, 1, 0, 1)
                        node.createReverseNode(remap.outValue, point_cns_target)
                
                # create a condition node for the orient constraint
                if orient_node:
                    for x, attr in enumerate(orient_con_targets):
                        node_name = pm.createNode("condition", name="orientConstraint_condition")
                        if space_attr_type == "enum":
                            pm.connectAttr(ctl.spaceSwitchOrient, node_name + ".firstTerm")
                            pm.setAttr(node_name + ".colorIfTrueR", 1)
                            pm.setAttr(node_name + ".secondTerm", x)
                            pm.setAttr(node_name + ".operation", 0)
                        elif space_attr_type == "float":
                            pm.connectAttr(orient_attr_list[x], node_name + ".firstTerm")
                            pm.connectAttr(orient_attr_list[x], node_name + ".colorIfTrueR")
                            pm.setAttr(node_name + ".secondTerm", 1)
                            pm.setAttr(node_name + ".operation", 5)
                        pm.setAttr(node_name + ".colorIfFalseR", 0)
                        pm.connectAttr(node_name + ".outColorR", attr)
                    if space_attr_type == "enum":
                        pass
                    elif space_attr_type == "float":
                        # create setup for the cns parent target
                        add = node.createPlusMinusAverage1D(orient_attr_list)
                        remap = node.createRemapValueNode(add.output1D, 0, 1, 0, 1)
                        node.createReverseNode(remap.outValue, orient_cns_target)

                # create a condition node for the orbit constraint
                if orbit_node:
                    for x, attr in enumerate(orbit_con_targets):
                        node_name = pm.createNode("condition", name="orbitConstraint_condition")
                        if space_attr_type == "enum":
                            pm.connectAttr(ctl.spaceSwitchOrbit, node_name + ".firstTerm")
                            pm.setAttr(node_name + ".colorIfTrueR", 1)
                            pm.setAttr(node_name + ".secondTerm", x)
                            pm.setAttr(node_name + ".operation", 0)
                        elif space_attr_type == "float":
                            pm.connectAttr(orbit_attr_list[x], node_name + ".firstTerm")
                            pm.connectAttr(orbit_attr_list[x], node_name + ".colorIfTrueR")
                            pm.setAttr(node_name + ".secondTerm", 1)
                            pm.setAttr(node_name + ".operation", 5)
                        pm.setAttr(node_name + ".colorIfFalseR", 0)
                        pm.connectAttr(node_name + ".outColorR", attr)
                    if space_attr_type == "enum":
                        pass
                    elif space_attr_type == "float":
                        # create setup for the cns parent target
                        add = node.createPlusMinusAverage1D(orbit_attr_list)
                        remap = node.createRemapValueNode(add.output1D, 0, 1, 0, 1)
                        node.createReverseNode(remap.outValue, orbit_cns_target)

                # create a condition node for the scale constraint
                if scale_node:
                    if parent_node:
                        if space_attr_type == "enum":
                            connection = ctl.spaceSwitchParent
                        elif space_attr_type == "float":
                            connection = parent_attr_list
                    elif point_node:
                        if space_attr_type == "enum":
                            connection = ctl.spaceSwitchPoint
                        elif space_attr_type == "float":
                            connection = point_attr_list
                    elif orbit_node:
                        if space_attr_type == "enum":
                            connection = ctl.spaceSwitchOrbit
                        elif space_attr_type == "float":
                            connection = orbit_attr_list
                    elif not point_node and not orbit_node and orient_node:
                        if space_attr_type == "enum":
                            connection = ctl.spaceSwitchOrient
                        elif space_attr_type == "float":
                            connection = orient_attr_list

                    for x, attr in enumerate(scale_con_targets):
                        node_name = pm.createNode("condition", name="scaleConstraint_condition")
                        if space_attr_type == "enum":
                            pm.connectAttr(connection, node_name + ".firstTerm")
                            pm.setAttr(node_name + ".colorIfTrueR", 1)
                            pm.setAttr(node_name + ".secondTerm", x)
                            pm.setAttr(node_name + ".operation", 0)
                        elif space_attr_type == "float":
                            pm.connectAttr(connection[x], node_name + ".firstTerm")
                            pm.connectAttr(connection[x], node_name + ".colorIfTrueR")
                            pm.setAttr(node_name + ".secondTerm", 1)
                            pm.setAttr(node_name + ".operation", 5)
                        pm.setAttr(node_name + ".colorIfFalseR", 0)
                        pm.connectAttr(node_name + ".outColorR", attr)
                    if space_attr_type == "enum":
                        pass
                    elif space_attr_type == "float":
                        # create setup for the cns parent target
                        add = node.createPlusMinusAverage1D(connection)
                        remap = node.createRemapValueNode(add.output1D, 0, 1, 0, 1)
                        node.createReverseNode(remap.outValue, scale_cns_target)


            return [parent_node, point_node, orient_node, orbit_node, scale_node]
        
        else:
            return None