from __main__ import *
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel
import types, sys
from rigging_utils.controls import cv_data
from rigging_utils import conversions
reload(cv_data)
reload(conversions)


'''
/////////////// UTILITIES ///////////////
'''

def freeze(self):
    mel.eval('FreezeTransformations')

def center_pivot(self):
    mel.eval('CenterPivot')

def delete_history(self):
    mel.eval('DeleteHistory')

def draw_curve(self):
    mel.eval('CVCurveToolOptions')

'''
/////////////// JOINTS ///////////////
'''

def joint_size_set(value):
    pm.jointDisplayScale(value)

def draw_joint(self):
    mel.eval('JointTool')

def split_joint(value):
    axis = pm.confirmDialog(message="Choose The Up Axis", button=["X", "Y", "Z"], cancelButton="Cancel", ds=True)

    if pm.ls(sl=True, type="joint"):
        selected_bone = pm.ls(sl=True)[0]
        child_bone = selected_bone.getChildren()[0]
        if axis == "X":
            trans = child_bone.tx.get()
            up_axis = "tx"
        if axis == "Y":
            trans = child_bone.ty.get()
            up_axis = "ty"
        if axis == "Z":
            trans = child_bone.tz.get()
            up_axis = "tz"

        bone_radius = selected_bone.radius.get()

        new_trans = trans/(value+1)


        for i in range(value):
            new_jnt = pm.insertJoint(selected_bone)
            pm.setAttr(new_jnt+".radius", bone_radius)
            pm.setAttr(new_jnt+"."+up_axis, new_trans)
        
        pm.setAttr(child_bone+"."+up_axis, new_trans)

def mirror_joints(self):

    if pm.ls(sl=True)[0].startswith('_L_') == True:
        replacee = '_L_'
        replacement = '_R_'
    elif pm.ls(sl=True)[0].startswith('_R_') == True:
        replacee = '_R_'
        replacement = '_L_'
    else:
        replacee = ''
        replacement = ''
    pm.mirrorJoint(mirrorYZ=True, mirrorBehavior=True, searchReplace=(replacee, replacement))

def sc_ik(self):

    first = pm.ls(sl=True)[0]
    second = pm.ls(sl=True)[1]
    name = first+'_ikHandle'
    pm.ikHandle(n=name, sj=first, ee=second, solver='ikSCsolver')

def rp_ik(self):

    first = pm.ls(sl=True)[0]
    second = pm.ls(sl=True)[1]
    name = first+'_ikHandle'
    pm.ikHandle(n=name, sj=first, ee=second, solver='ikRPsolver')

def load_ctrl(self):

    sel = pm.selected()[0]
    pm.textField('ctrlName', edit=True, text=str(sel))

def ikfk(self):

    chain = pm.ls(sl=True, dag=True, type='joint')

    # Check if ikfk was already created. If True, only create SDK's on IKFK control.
    if pm.joint(exists=chain[0].replace('_Jnt', 'IK_Jnt')) and pm.joint(exists=chain[0].replace('_Jnt', 'IK_Jnt')) == True:
        pass



    ikChain = pm.duplicate()
    fkChain = pm.duplicate()

    # Setup IK joint chain
    pm.select(ikChain)
    ikChain = pm.ls(sl=True, dag=True)
    for jnt in ikChain:
        if jnt.endswith('_Jnt1') == True:
            pm.rename(jnt, jnt.replace('_Jnt1', 'IK_Jnt'))
        else:
            pm.rename(jnt, jnt.replace('_Jnt', 'IK_Jnt'))
        if jnt.endswith('_Jx') == True:
            pm.rename(jnt, jnt.replace('_Jx', 'IK_Jx'))
    pm.ikHandle(n=ikChain[0].replace('Jnt', 'ikHandle'), sj=ikChain[0], ee=ikChain[-1], solver='ikRPsolver')

    # Setup FK joint chain
    pm.select(fkChain)
    fkChain = pm.ls(sl=True, dag=True)
    for jnt in fkChain:
        if jnt.endswith('_Jnt2') == True:
            pm.rename(jnt, jnt.replace('_Jnt2', 'FK_Jnt'))
        else:
            pm.rename(jnt, jnt.replace('_Jnt', 'FK_Jnt'))
        if jnt.endswith('_Jx') == True:
            pm.rename(jnt, jnt.replace('_Jx', 'FK_Jx'))    
        
    # Constrain bind joints to IK and FK joints
    for jnt in chain:
        pm.parentConstraint(ikChain[chain.index(jnt)], fkChain[chain.index(jnt)], jnt)

    # Add attr on control
    ctrl = pm.textField('ctrlName', q=True, text=True)
    try:
        pm.addAttr(ctrl, ln='IKFK', keyable=True, hnv=True, hxv=True, min=0, max=1)
        # Create SDK's on control
        for jnt in chain:
            con = jnt+'_parentConstraint1'
            pm.setAttr(ctrl+'.IKFK', 0)
            pm.setAttr(con+'.'+str(ikChain[chain.index(jnt)])+'W0', 1) 
            pm.setAttr(con+'.'+str(fkChain[chain.index(jnt)])+'W1', 0)
            pm.setDrivenKeyframe(con+'.'+str(ikChain[chain.index(jnt)])+'W0', currentDriver=ctrl+'.IKFK')
            pm.setDrivenKeyframe(con+'.'+str(fkChain[chain.index(jnt)])+'W1', currentDriver=ctrl+'.IKFK')

            pm.setAttr(ctrl+'.IKFK', 1)
            pm.setAttr(con+'.'+str(ikChain[chain.index(jnt)])+'W0', 0) 
            pm.setAttr(con+'.'+str(fkChain[chain.index(jnt)])+'W1', 1)
            pm.setDrivenKeyframe(con+'.'+str(ikChain[chain.index(jnt)])+'W0', currentDriver=ctrl+'.IKFK')
            pm.setDrivenKeyframe(con+'.'+str(fkChain[chain.index(jnt)])+'W1', currentDriver=ctrl+'.IKFK')
    except:
        raise

def joint_to_selected(self):

    sel = pm.ls(sl=True)
    if sel == []:
        pm.joint()
    else:
        try:
            for i in sel:
                pm.select(d=True)
                trans = pm.xform(i, translation=True, ws=True, q=True)
                rots = pm.xform(i, rotation=True, ws=True, q=True)
                jnt = pm.joint(o=rots, p=trans)
        except:
            raise

'''
/////////////// BINDING ///////////////
'''

def smooth_bind(self):

    mel.eval('SmoothBindSkin')

def detach_skin(self):

    mel.eval('DetachSkin')

def copy_skin(self):
    
    source = pm.ls(sl=True)[0] 
    shapes = pm.ls(sl=True, dag=True, type='shape')
    dest = pm.ls(sl=True)[1]

    # Select influences from source geo
    for jnt in pm.skinCluster(source, inf=True, q=True):
        pm.select(jnt, add=True)
    pm.select(dest, add=True)

    # Skin source geo to influences
    try:
        mel.eval('SmoothBindSkin')
    except:
        pass

    # Copy weights from source to dest
    pm.copySkinWeights(ss=shapes[0], ds=shapes[1])

def paint_skin(self):
    
    mel.eval('ArtPaintSkinWeightsToolOptions')

def smooth_skin(self):

    mel.eval('SmoothSkinWeights')

def mirror_skin():
    pass

def lock_weights(self):

    for sel in pm.ls(sl=True, type='joint'):
        sel.liw.set(1)
    paint_skin(self)

def unlock_weights(self):
    
    for sel in pm.ls(sl=True, type='joint'):
        sel.liw.set(0)
    paint_skin(self)

def lock_all_weights(self):
    
    sel = pm.ls(sl=True)[0]
    for jnt in pm.skinCluster(sel, inf=True, q=True):
        jnt.liw.set(1)
    paint_skin(self)

def unlock_all_weights(self):
    
    sel = pm.ls(sl=True)[0]
    for jnt in pm.skinCluster(sel, inf=True, q=True):
        jnt.liw.set(0)
    paint_skin(self)

def select_influences(self):
    
    sel = pm.ls(sl=True)
    pm.select(d=True)
    for i in sel:
        for jnt in pm.skinCluster(sel, inf=True, q=True):
            pm.select(jnt, add=True)

def select_skin_cluster(self):
    sel = pm.ls(sl=True, dag=True, type='shape')
    pm.select(pm.listConnections(sel, type='skinCluster'))

'''
/////////////// CONTROLS ///////////////
'''

def color_dict():

    # Dictionary that contains all colors
    color_dict = {  'Grey':0,
                    'Black':1,
                    'Dark Grey':2,
                    'Light Grey':3,
                    'Dark Red':4,
                    'Dark Blue':5,
                    'Blue':6,
                    'Dark Green':7,
                    'Dark Purple':8,
                    'Pink':9,
                    'Brown':10,
                    'Dark Brown':11,
                    'Dark Orange':12,
                    'Red':13,
                    'Green':14,
                    'Blue2':15,
                    'White':16,
                    'Yellow':17,
                    'Light Blue':18,
                    'Light Green':19,
                    'Light Pink':20,
                    'Light Brown':21,
                    'Light Yellow':22,
                    'Green2':23,
                    'Brown2':24,
                    'Dirty Yellow':25,
                    'Dirty Green':26,
                    'Green3':27,
                    'Blue4':28,
                    'Blue5':29,
                    'Purple':30,
                    'Dark Pink':31  }

    return color_dict

def control_dict():

    cntDict = {
    "Ball": [[1.8746997283273217e-32, 5.0, -3.061616997868383e-16], [1.5308084989341943e-16, 4.330127018922191, -2.5000000000000044], [2.651438096812269e-16, 2.499999999999996, -4.330127018922195], [3.6940426609234065e-15, -3.061616997868383e-16, -5.0], [2.651438096812266e-16, -2.5000000000000036, -4.330127018922191], [1.5308084989341896e-16, -4.3301270189221945, -2.499999999999997], [-1.8870088146413462e-31, -5.0, 3.0817192613497296e-15], [-1.5308084989341928e-16, -4.330127018922193, 2.500000000000002], [-2.651438096812268e-16, -2.4999999999999982, 4.3301270189221945], [-9.184850993605148e-16, 3.061616997868383e-16, 5.0], [-2.651438096812267e-16, 2.500000000000001, 4.330127018922193], [-1.5308084989341913e-16, 4.330127018922194, 2.4999999999999996], [1.8746997283273217e-32, 5.0, -3.061616997868383e-16], [-2.4999999999999996, 4.330127018922194, 0.0], [-4.330127018922193, 2.500000000000001, 0.0], [-5.0, -2.7367782355456534e-31, -5.0818214417048514e-15], [-4.3301270189221945, -2.4999999999999982, 0.0], [-2.500000000000002, -4.330127018922193, 0.0], [-1.8870088146413462e-31, -5.0, 3.0817192613497296e-15], [2.499999999999997, -4.3301270189221945, 0.0], [4.330127018922191, -2.5000000000000036, 0.0], [5.0, 1.0372393937370392e-31, 2.306263880141961e-15], [4.330127018922195, 2.499999999999996, 0.0], [2.5000000000000044, 4.330127018922191, 0.0], [1.8746997283273217e-32, 5.0, -3.061616997868383e-16], [-1.5308084989341913e-16, 4.330127018922194, 2.4999999999999996], [-2.651438096812267e-16, 2.500000000000001, 4.330127018922193], [-9.184850993605148e-16, 3.061616997868383e-16, 5.0], [-2.500000000000005, 2.651438096812266e-16, 4.33012701892219], [-4.330127018922196, 1.530808498934189e-16, 2.499999999999995], [-5.0, -2.7367782355456534e-31, -5.0818214417048514e-15], [-4.330127018922191, -1.5308084989341938e-16, -2.500000000000004], [-2.4999999999999964, -2.6514380968122684e-16, -4.330127018922195], [3.6940426609234065e-15, -3.061616997868383e-16, -5.0], [2.5000000000000027, -2.6514380968122664e-16, -4.330127018922192], [4.3301270189221945, -1.5308084989341906e-16, -2.499999999999998], [5.0, 1.0372393937370392e-31, 2.306263880141961e-15], [4.330127018922193, 1.530808498934192e-16, 2.5000000000000018], [2.499999999999999, 2.6514380968122674e-16, 4.3301270189221945], [-9.184850993605148e-16, 3.061616997868383e-16, 5.0]],
    "Diamond": [[0.0, 6.427516017256561, 0.0], [-4.9560637093959725, 0.0, -4.9560637093959725], [-4.9560637093959725, 0.0, 4.9560637093959725], [0.0, 6.427516017256561, 0.0], [4.9560637093959725, 0.0, 4.9560637093959725], [-4.9560637093959725, 0.0, 4.9560637093959725], [0.0, -6.427516017256561, 0.0], [4.9560637093959725, 0.0, 4.9560637093959725], [4.9560637093959725, 0.0, -4.9560637093959725], [0.0, -6.427516017256561, 0.0], [-4.9560637093959725, 0.0, -4.9560637093959725], [4.9560637093959725, 0.0, -4.9560637093959725], [0.0, 6.427516017256561, 0.0]],
    "Cube": [[5.0, 5.0, 5.0], [-5.0, 5.0, 5.0], [-5.0, 5.0, -5.0], [5.0, 5.0, -5.0], [5.0, 5.0, 5.0], [5.0, 5.0, -5.0], [5.0, -5.0, -5.0], [5.0, -5.0, 5.0], [5.0, 5.0, 5.0], [5.0, -5.0, 5.0], [-5.0, -5.0, 5.0], [-5.0, 5.0, 5.0], [-5.0, -5.0, 5.0], [-5.0, -5.0, -5.0], [-5.0, 5.0, -5.0], [-5.0, -5.0, -5.0], [5.0, -5.0, -5.0]],
    "Double Arrow": [[-1.9999999999999998, 0.0, -0.5483701142510383], [1.9999999999999998, 0.0, -0.548370114251039], [1.9999999999999998, 0.0, -1.0967402290018784], [3.6892379367706196, 0.0, -2.366933553298662e-10], [1.9999999999999998, 0.0, 1.096740228502078], [1.9999999999999998, 0.0, 0.5483701137512385], [-1.9999999999999998, 0.0, 0.5483701137512385], [-1.9999999999999998, 0.0, 1.096740228502078], [-3.6892379367706196, 0.0, -2.366933553298662e-10], [-1.9999999999999998, 0.0, -1.0967402290018784], [-1.9999999999999998, 0.0, -0.548370114251039]],
    "Fourway Arrow": [[-3.9023781856840563, 0.0, -0.5483701142510383], [-0.548370114251039, 0.0, -0.5483701142510383], [-0.548370114251039, 0.0, -3.9023781856840563], [-1.0967402290018784, 0.0, -3.9023781856840563], [0.0, 0.0, -4.999118414685935], [1.0967402290018784, 0.0, -3.9023781856840563], [0.548370114251039, 0.0, -3.9023781856840563], [0.5483701142510387, 0.0, -0.5483701142510391], [3.9023781856840563, 0.0, -0.548370114251039], [3.9023781856840563, 0.0, -1.0967402290018784], [4.999118414685935, 0.0, -2.366933553298662e-10], [3.9023781856840563, 0.0, 1.096740228502078], [3.9023781856840563, 0.0, 0.5483701137512385], [0.5483701142510387, 0.0, 0.5483701137512388], [0.548370114251039, 0.0, 3.394730573564863], [0.548370114251039, 0.0, 3.9023781856840563], [1.0967402290018784, 0.0, 3.9023781856840563], [0.0, 0.0, 4.999118414685935], [-1.0967402290018784, 0.0, 3.9023781856840563], [-0.548370114251039, 0.0, 3.9023781856840563], [-0.548370114251039, 0.0, 0.5483701137512376], [-3.9023781856840563, 0.0, 0.5483701137512385], [-3.9023781856840563, 0.0, 1.096740228502078], [-4.999118414685935, 0.0, -2.366933553298662e-10], [-3.9023781856840563, 0.0, -1.0967402290018784], [-3.9023781856840563, 0.0, -0.548370114251039]],
    "Burst": [[2.722399353266438e-17, 1.0, 0.0], [-0.13431175833561235, 0.3871974891818899, 0.0], [-0.6506701427414181, 0.7598966551467238, 0.0], [-0.3393849066098479, 0.19507321321834714, 0.0], [-0.9955558203229323, 0.1750939914622614, 0.0], [-0.3877209583568725, -0.0706943668617964, 0.0], [-0.8714427523781003, -0.5033323588263805, 0.0], [-0.2534046270113447, -0.30382561725878765, 0.0], [-0.3448739354083346, -0.9494503586609591, 0.0], [-7.052192681028207e-17, -0.3945818776987219, 0.0], [0.3448739354083353, -0.9494462214246226, 0.0], [0.2534046270113447, -0.30383157792572524, 0.0], [0.8714427523781002, -0.5032740501237176, 0.0], [0.3877209583568725, -0.07079096249083902, 0.0], [0.9955558203229323, 0.1759578216742299, 0.0], [0.3393849066098479, 0.19379696913402095, 0.0], [0.6506701427414184, 0.7738065176137146, 0.0], [0.13431175833561207, 0.3682682966341111, 0.0], [2.722399353266438e-17, 1.0, 0.0], [-0.13431175833561235, 0.3871974891818899, 0.0], [-0.6506701427414181, 0.7598966551467238, 0.0]],
    "Arched Pin Arrow": [[-3.234097285778847, -2.329312554467163e-16, -6.0099832485428895], [-2.9004992201852806, -1.6123167451268806e-16, -6.288135693605273], [-2.5343033626889286, -1.0241860168944811e-16, -6.54085025744459], [-2.14623625669435, -5.624962685519431e-17, -6.758492114790499], [-1.739646953555913, -2.2398170346626703e-17, -6.939182998338577], [-1.318044352575898, -4.3135128856026334e-19, -7.0813635308005525], [-0.8850669199797271, 1.0186276575855276e-17, -7.183806682184679], [-0.4444512857454333, 1.0088104016818558e-17, -7.245628359876216], [1.2165785434171253e-17, -3.228479694735555e-32, -7.266295037488169], [0.4444512854462349, -1.9265952531827787e-17, -7.245628359904101], [0.8850669199498966, -4.6818465102272995e-17, -7.183806682190288], [1.3180443528647903, -8.169473541851478e-17, -7.081363530717858], [1.739646953555913, -1.2286875665175812e-16, -6.939182998338577], [2.146236258270177, -1.692601720377509e-16, -6.758492114000594], [2.5343033636860803, -2.1974359760763205e-16, -6.54085025682277], [2.9004992206528537, -2.7315833569165104e-16, -6.28813569324944], [3.234097285778848, -3.249832542313111e-16, -6.00998324854289], [3.71230889662317, -4.716625375244234e-16, -6.545770375378218], [4.186536411752846, -3.5370664145461765e-16, -4.197282664010606], [1.7994624545534497, 1.1505459524696213e-16, -4.402621869501902], [2.2776740653977714, -3.162468804615016e-17, -4.93840899633723], [2.0306610810795545, -1.4880303539971376e-17, -5.145157843325002], [1.7742846390096816, -2.678516556383624e-18, -5.322085188150596], [1.5025959705125442, 7.471036848770262e-18, -5.474457872070301], [1.2179397739299298, 1.4755743296552254e-17, -5.600960904214836], [0.9227726566642858, 1.8387713404855864e-17, -5.700502552683862], [0.6196419347337843, 1.761058124228385e-17, -5.7722237651438775], [0.31116365144421065, 1.1706031773409472e-17, -5.815505581574781], [1.2165785434171253e-17, -3.228479694735555e-32, 0.0], [-0.3111636521900534, -1.8131511853842652e-17, -5.81550558150527], [-0.6196419332614358, -4.3257048792167285e-17, -5.772223765420728], [-0.9227726559441343, -7.588479757622658e-17, -5.700502552890005], [-1.2179397739299298, -1.1645819957152433e-16, -5.600960904214836], [-1.5025959712607373, -1.6535212485522647e-16, -5.474457871695259], [-1.774284637646744, -2.2286963579279814e-16, -5.32208518900052], [-2.030661083023741, -2.89239374448322e-16, -5.145157841845421], [-2.2776740653977714, -3.6430992148283946e-16, -4.93840899633723], [-1.7994624545534497, -4.299992545907078e-16, -4.402621869501902], [-4.186536411752846, -6.902814069420573e-16, -4.197282664010606], [-3.71230889662317, -1.6724192233884753e-16, -6.545770375378218], [-3.234097285778848, -2.3293125544671605e-16, -6.00998324854289]],
    "Arched Arrow": [[-2.7719897180527453, -1.99648615380449e-16, -3.5793026023004733], [-2.486058181035004, -1.3819390837093088e-16, -3.8177109276018184], [-2.172186623665035, -8.778440650777116e-17, -4.03431609147402], [-1.8395689153290289, -4.821233670753729e-17, -4.220859951312012], [-1.4910755744743942, -1.9197783003330708e-17, -4.3757326181126075], [-1.1297141274456135, -3.6971718260166675e-19, -4.497597527936107], [-0.7586031541971934, 8.730799180863972e-18, -4.585402976328279], [-0.38094537219988595, 8.646654116508195e-18, -4.638391195225485], [5.353399977458467e-33, -2.767174802718966e-32, -4.656104891748639], [0.38094537194343886, -1.6513115595363946e-17, -4.638391195249387], [0.7586031541716255, -4.012875693294361e-17, -4.585402976333087], [1.129714127693227, -7.002169279042769e-17, -4.497597527865228], [1.4910755744743942, -1.0531251845956021e-16, -4.3757326181126075], [1.839568916679692, -1.4507524514726924e-16, -4.220859950634974], [2.1721866245197075, -1.8834529061780643e-16, -4.034316090941049], [2.4860581814357676, -2.3412780477174396e-16, -3.8177109272968277], [2.7719897180527457, -2.7854766250532564e-16, -3.579302602300474], [3.181871533959427, -4.042685141716464e-16, -4.038533192914844], [3.5883385260742267, -3.0316687677595587e-16, -2.0256117457121547], [1.5423442714534383, 9.861489214987959e-17, -2.201610831713032], [1.9522260873601192, -2.7105959516441203e-17, -2.660841422327402], [1.7405078265129579, -1.2754114910421137e-17, -2.8380487316404075], [1.520764015931364, -2.295793755672808e-18, -2.9896956171115137], [1.287895883331532, 6.403529485352813e-18, -3.120296361558756], [1.0439131022393477, 1.2647352595151822e-17, -3.2287238680376458], [0.7909212649914485, 1.576036463741881e-17, -3.3140423979679263], [0.5311037115393119, 1.509427386343675e-17, -3.3755156456589153], [0.26670268894752175, 1.0033402476102482e-17, -3.4126130918775814], [5.35339997745847e-33, -2.767174802718966e-32, -3.425014582582052], [-0.26670268958679394, -1.5540770728391807e-17, -3.412613091818001], [-0.5311037102773416, -3.707621753138355e-17, -3.375515645896208], [-0.7909212643741969, -6.504191434277039e-17, -3.3140423981446148], [-1.0439131022393477, -9.981794091808133e-17, -3.2287238680376458], [-1.2878958839728187, -1.4172560360888434e-16, -3.1202963612373025], [-1.5207640147631718, -1.9102466137935536e-16, -2.9896956178399945], [-1.7405078281793471, -2.4791108651936294e-16, -2.838048730372239], [-1.9522260873601192, -3.122550954096716e-16, -2.660841422327402], [-1.5423442714534383, -3.685583355012576e-16, -2.201610831713032], [-3.5883385260742267, -5.916497846308793e-16, -2.0256117457121547], [-3.181871533959427, -1.4334537528886272e-16, -4.038533192914844], [-2.7719897180527457, -1.9964861538044878e-16, -3.579302602300474]],
    "Triangle Bot": [[0.0, 0.0, -1.409790015236395], [1.522174917159727, 0.0, 0.9343596247512762], [-1.522174917159727, 0.0, 0.9343596247512762], [0.0, 0.0, -1.409790015236395], [0.0, 4.5665247514791805, 8.449768202688096e-17], [1.522174917159727, 0.0, 0.9343596247512762], [-1.522174917159727, 0.0, 0.9343596247512762], [0.0, 4.5665247514791805, 8.449768202688096e-17]],
    "Triangle Wedge": [[0.0, -4.613708280098827, -1.409790015236395], [1.522174917159727, -4.613708280098827, 0.9343596247512762], [-1.522174917159727, -4.613708280098827, 0.9343596247512762], [0.0, -4.613708280098827, -1.409790015236395], [0.0, -0.04718352861964625, 8.449768202688096e-17], [1.522174917159727, -4.613708280098827, 0.9343596247512762], [-1.522174917159727, -4.613708280098827, 0.9343596247512762], [0.0, -0.04718352861964625, 8.449768202688096e-17]],
    "Arrow": [[0, 0, 4], [2, 0, 4], [2, 0, 1], [3, 0, 2], [1, 0, -2], [-1, 0, 2], [0, 0, 1], [0, 0, 4]],
    "Pin": [[-3.0, 0.0, -3.0], [3.0, 0.0, -3.0], [3.0, 0.0, 3.0], [-3.0, 0.0, 3.0], [-3.0, 0.0, -3.0], [-3.0, 0.0, 3.0], [0.0, 0.0, 3.0], [0.0, 0.0, 12.0]],
    }

    return cntDict

def view_color(self):

    colors = color_dict()
    selColor = pm.optionMenu('Colors', value=True, q=True)
    color = pm.colorIndex(colors[selColor], q=True)
    pm.optionMenu('Colors', edit=True, bgc=color)

def update_color(control_color):

    for obj in pm.ls(sl=True, type="transform"):
        for shape in obj.getShapes():
            shape.overrideEnabled.set(True)
            shape.overrideRGBColors.set(True)
            rgb = conversions.rgb_to_parametric(control_color)
            shape.overrideColorRGB.set(rgb)

def create_control(control_name, control_color):

    control_dict = cv_data.get_control_dict()

    sel = pm.ls(sl=True)
    if sel:
        for obj in sel:
            if obj.type() == "joint":

                # create a transform for the curve
                grp = pm.group(name=obj.replace("jnt", "null"), empty=True)
                tmp = pm.parentConstraint(obj, grp)
                pm.delete(tmp)

                # create the curve
                crv = pm.curve(name=obj.replace("jnt", "ctl"), degree=1, p=control_dict[control_name])
                crv_shape = crv.getShape()
                crv_shape.overrideEnabled.set(True)
                crv_shape.overrideRGBColors.set(True)
                rgb = conversions.rgb_to_parametric(control_color)
                crv_shape.overrideColorRGB.set(rgb)

                # parent the curve shape under the transform
                pm.parent(crv, grp, r=True)
            
            else:

                # create a transform for the curve
                grp = pm.group(name=control_name+"_adj", empty=True)
                tmp = pm.parentConstraint(obj, grp)
                pm.delete(tmp)

                # create the curve
                crv = pm.curve(name=control_name+"_ctl", degree=1, p=control_dict[control_name])
                crv_shape = crv.getShape()
                crv_shape.overrideEnabled.set(True)
                crv_shape.overrideRGBColors.set(True)
                rgb = conversions.rgb_to_parametric(control_color)
                crv_shape.overrideColorRGB.set(rgb)

                # parent the curve shape under the transform
                pm.parent(crv, grp, r=True)
        
    else:
        # create a transform for the curve
        grp = pm.group(name=control_name+"_adj", empty=True)

        # create the curve
        crv = pm.curve(name=control_name+"_ctl", degree=1, p=control_dict[control_name])
        crv_shape = crv.getShape()
        crv_shape.overrideEnabled.set(True)
        crv_shape.overrideRGBColors.set(True)
        rgb = conversions.rgb_to_parametric(control_color)
        crv_shape.overrideColorRGB.set(rgb)

        # parent the curve shape under the transform
        pm.parent(crv, grp, r=True)




    

def constrain_joints(self):

    # Parent Constrains all joints to their respective controls if they are created.
    pm.select('*_Ctrl')
    ctrls = ['World_Ctrl', 'WorldOffset_Ctrl', 'All_Ctrl', 'Cog_Ctrl']
    for ctrl in ctrls:
        pm.select(ctrl, d=True)
    sel = pm.ls(sl=True)
    for i in sel:
        try:
            if pm.objExists(i.replace('Ctrl', 'SubCtrl')) == False:
                pm.parentConstraint(i, i.replace('_Ctrl', '_Jnt'), mo=True)
            else:
                pm.parentConstraint(i.replace('Ctrl', 'SubCtrl'), i.replace('Ctrl', 'Jnt'))
        except:
            raise

'''
/////////////// CONSTRAINTS ///////////////
'''

def create_constraint(offset, exclude_trans, exclude_rots, con_type):

    # Get selected
    sel = pm.ls(sl=True)

    # Set variables to whether attributes are excluded or not
    if exclude_trans:
        tran = ["x", "y", "z"]
    else:
        tran = "none"

    if exclude_rots:
        rot = ["x", "y", "z"]
    else:
        rot = "none"

    # Create the consraint
    if con_type == 'Parent':
        for i in sel:
            if i != sel[-1]:
                pm.parentConstraint(i, sel[-1], mo=offset, st=tran, sr=rot)

    if con_type == 'Orient':
        for i in sel:
            if i != sel[-1]:
                pm.orientConstraint(i, sel[-1], mo=offset)

    if con_type == 'Scale':
        for i in sel:
            if i != sel[-1]:
                pm.scaleConstraint(i, sel[-1], mo=offset)

    if con_type == 'Point':
        for i in sel:
            if i != sel[-1]:
                pm.pointConstraint(i, sel[-1], mo=offset)

    if con_type == 'Aim':
        for i in sel:
            if i != sel[-1]:
                pm.aimConstraint(i, sel[-1], mo=offset)

    if con_type == 'Pole Vector':
        pm.poleVectorConstraint(sel[0], sel[-1])

'''
/////////////// RENAMER ///////////////
'''
# TODO utilize having ###'s in the name and have the renamer iterate the numbers anywhere in the name and combine with letters if they want to. 
def rename(name, dag):

    # get the selection
    if dag:
        sel = pm.ls(sl=True, dag=True)
    else:
        sel = pm.ls(sl=True)

    # get the split name
    split = name.split("_")

    # replace all # symbols with number iterations
    split_index = None
    if "#" in name:
        for i in split:
            number_list = []
            if "#" in i:
                number_length = len(i)
                split_index = split.index(i)
                number_list.append(split_index)
                split.pop(split_index)
                split.insert(split_index, "1".zfill(number_length))

    for i in sel:
        if number_list:
            for x in number_list:
                if sel.index(i) != 0:
                    new_number = str(int(split[x])+1).zfill(number_length)
                    split.pop(x)
                    split.insert(x, new_number)
                    newName = "_".join(split)
                else:
                    newName = "_".join(split)
        else:
            newName = "_".join(split)
        i.rename(newName)

def rename_with_pound(name, dag):

    def store_split_info(obj_name):
        # dict will look like this {split_part_index:split_part_name}
        split_dict = {}    
        split = obj_name.split("_")
        for idx, i in enumerate(split):
            split_dict[idx] = i
        return split_dict

    def all_pound_convert(part_name, current_index):
        part_length = len(part_name)
        return str(current_index).zfill(part_length)

    def partial_pound_convert(split_index, part_name, char_value, char_index, current_index):
        number_of_pounds = part_name.count("#")
        
        if char_value == "#":
            normal_fill_value = 1
            for idx, char in enumerate(part_name[char_index+1:]):
                if char == "#":
                    normal_fill_value = normal_fill_value+1
                else:
                    break
            
            reverse_fill_value = 1
            reversed_name = part_name[::-1]
            for idx, char in enumerate(reversed_name[-char_index:]):
                if char == "#":
                    reverse_fill_value = reverse_fill_value+1
                else:
                    break
                    
            
            reverse = False
            
            if normal_fill_value > reverse_fill_value:
                fill_value = normal_fill_value
            elif reverse_fill_value > normal_fill_value:
                fill_value = reverse_fill_value
                reverse = True
            elif normal_fill_value == reverse_fill_value:
                fill_value = normal_fill_value
            else:
                fill_value = reverse_fill_value
                reverse = True
                
            
            if not reverse:
                end_index = char_index+fill_value
                current_replace = part_name[char_index:end_index] 
                new_part_name = part_name.replace(current_replace, str(current_index).zfill(fill_value))
                split_dict.pop(split_index)
                split_dict.update({split_index:new_part_name})
            
            else:
                end_index = char_index+fill_value
                current_replace = part_name[char_index:end_index] 
                new_part_name = part_name.replace(current_replace, str(current_index).zfill(fill_value))
                split_dict.pop(split_index)
                split_dict.update({split_index:new_part_name})

    # get the selection
    if dag:
        sel = pm.ls(sl=True, dag=True)
    else:
        sel = pm.ls(sl=True)

    x=1
    for i in sel:
        rename_split_list = []
        # store the split info into a dict
        split_dict = store_split_info(name)
    
        for split_index in split_dict:
            part_name = split_dict[split_index]
            
            # if all the characters of part_name = "#"
            if part_name == len(part_name) * "#":
                new_part_name = all_pound_convert(part_name, x)
                # replace the current name with the new name in ther dict
                split_dict.pop(split_index)
                split_dict.update({split_index:new_part_name})
            
        for split_index in split_dict:
            part_name = split_dict[split_index]
            
            # do a partial replace for each character in the part name
            if "#" in part_name:
                for idx, char in enumerate(part_name):
                    partial_pound_convert(split_index, part_name, char, idx, x)
                    if "#" not in split_dict[split_index]:
                        break
            
            # convert to a list for the join function
            rename_split_list.insert(split_index, split_dict[split_index])
        
        i.rename("_".join(rename_split_list))
                
        x = x+1

def replace(name1, name2, dag):

    # Get Selection based on settings
    if dag:
        sel = pm.ls(sl=True, dag=True)    
    else:
        sel = pm.ls(sl=True)
        
    for i in sel:
        newName = i.replace(name1, name2)
        i.rename(newName)

'''
/////////////// ATTRIBUTES ///////////////
'''
# TODO need to fix some stuff up in the defaults and channelbox selection mode
def attr_defaults(self):

    '''
    THIS STILL NEEDS WORK
    '''

    # Get all attributes and print out their default values in a custom window
    attrWin = pm.window('Default Values', w=200, h=300)
    scroll = pm.scrollLayout()
    pm.text('WARNING: Only displays numeric only!', bgc=[1, 0, 0])
    for attr in sorted(pm.attributeInfo(pm.selected(), all=True)):
        try:
            pm.rowColumnLayout(nc=2, parent=scroll)
            pm.text(attr+'----------')
            pm.text(pm.attributeQuery(attr, n=pm.selected()[0], listDefault=True))
        except:
            pass
    pm.showWindow(attrWin)

def attr_keyable(attr_trans, attr_rots, attr_scales, attr_channel):
    
    sel = pm.ls(sl=True)

    trans = ['tx', 'ty', 'tz']
    rots = ['rx', 'ry', 'rz']
    scales = ['sx', 'sy', 'sz']

    # Sets translates to keyable or displayable if not already
    if attr_trans:
        for i in sel:
            for tran in trans:
                if pm.getAttr(i+'.'+tran, cb=True) == True:
                    pm.setAttr(i+'.'+tran, keyable=True)
                else:
                    pm.setAttr(i+'.'+tran, keyable=False, channelBox=True)

    # Sets rotates to keyable or displayable if not already
    if attr_rots:
        for i in sel:
            for rot in rots:
                if pm.getAttr(i+'.'+rot, cb=True) == True:
                    pm.setAttr(i+'.'+rot, keyable=True)
                else:
                    pm.setAttr(i+'.'+rot, keyable=False, channelBox=True)

    # Sets scales to keyable or displayable if not already    
    if attr_scales:
        for i in sel:
            for scale in scales:
                if pm.getAttr(i+'.'+scale, cb=True) == True:
                    pm.setAttr(i+'.'+scale, keyable=True)
                else:
                    pm.setAttr(i+'.'+scale, keyable=False, channelBox=True)

    # Sets selected attributes to keyable or displayable if not already 
    if attr_channel:
        channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
        cb = pm.channelBox(channelBox, q=True, sma=True)[0]
        for i in sel:
            if pm.getAttr(i+'.'+str(cb), cb=True) == True:
                pm.setAttr(i+'.'+str(cb), keyable=True)
            else:
                pm.setAttr(i+'.'+str(cb), keyable=False, channelBox=True)

def attr_lock(attr_trans, attr_rots, attr_scales, attr_channel):
    
    sel = pm.ls(sl=True)

    trans = ['tx', 'ty', 'tz']
    rots = ['rx', 'ry', 'rz']
    scales = ['sx', 'sy', 'sz']

    # Sets translates to keyable or displayable if not already
    if attr_trans:
        for i in sel:
            for tran in trans:
                if pm.getAttr(i+'.'+tran, lock=True) == False:
                    pm.setAttr(i+'.'+tran, lock=True)
                else:
                    pm.setAttr(i+'.'+tran, lock=False)

    # Sets rotates to keyable or displayable if not already
    if attr_rots:
        for i in sel:
            for rot in rots:
                if pm.getAttr(i+'.'+rot, lock=True) == False:
                    pm.setAttr(i+'.'+rot, lock=True)
                else:
                    pm.setAttr(i+'.'+rot, lock=False)

    # Sets scales to keyable or displayable if not already    
    if attr_scales:
        for i in sel:
            for scale in scales:
                if pm.getAttr(i+'.'+scale, lock=True) == False:
                    pm.setAttr(i+'.'+scale, lock=True)
                else:
                    pm.setAttr(i+'.'+scale, lock=False)

    # Sets selected attributes to keyable or displayable if not already 
    if attr_channel:
        channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
        cb = pm.channelBox(channelBox, q=True, sma=True)[0]
        for i in sel:
            if pm.getAttr(i+'.'+str(cb), lock=True) == False:
                pm.setAttr(i+'.'+str(cb), lock=True)
            else:
                pm.setAttr(i+'.'+str(cb), lock=False)

def attr_hide(attr_trans, attr_rots, attr_scales, attr_channel):

    sel = pm.ls(sl=True)

    trans = ['tx', 'ty', 'tz']
    rots = ['rx', 'ry', 'rz']
    scales = ['sx', 'sy', 'sz']

    # Sets translates to keyable or displayable if not already
    if attr_trans:
        for i in sel:
            for tran in trans:
                if pm.getAttr(i+'.'+tran, keyable=True) == False:
                    pm.setAttr(i+'.'+tran, keyable=True)
                else:
                    pm.setAttr(i+'.'+tran, keyable=False)

    # Sets rotates to keyable or displayable if not already
    if attr_rots:
        for i in sel:
            for rot in rots:
                if pm.getAttr(i+'.'+rot, keyable=True) == False:
                    pm.setAttr(i+'.'+rot, keyable=True)
                else:
                    pm.setAttr(i+'.'+rot, keyable=False)

    # Sets scales to keyable or displayable if not already    
    if attr_scales:
        for i in sel:
            for scale in scales:
                if pm.getAttr(i+'.'+scale, keyable=True) == False:
                    pm.setAttr(i+'.'+scale, keyable=True)
                else:
                    pm.setAttr(i+'.'+scale, keyable=False)

    # Sets selected attributes to keyable or displayable if not already 
    if attr_channel:
        channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
        cb = pm.channelBox(channelBox, q=True, sma=True)[0]
        for i in sel:
            if pm.getAttr(i+'.'+str(cb), keyable=True) == False:
                pm.setAttr(i+'.'+str(cb), keyable=True)
            else:
                pm.setAttr(i+'.'+str(cb), keyable=False)

def attr_unhide(self):

    sel = pm.ls(sl=True)

    trans = ['tx', 'ty', 'tz']
    rots = ['rx', 'ry', 'rz']
    scales = ['sx', 'sy', 'sz']

    # Sets translates to keyable or displayable if not already
    for i in sel:
        for tran in trans:
            pm.setAttr(i+'.'+tran, keyable=True)

    # Sets rotates to keyable or displayable if not already
    for i in sel:
        for rot in rots:
            pm.setAttr(i+'.'+rot, keyable=True)

    # Sets scales to keyable or displayable if not already    
    for i in sel:
        for scale in scales:
            pm.setAttr(i+'.'+scale, keyable=True)

def attr_unhide_custom(self):
    sel = pm.ls(sl=True)
    # Sets translates to keyable or displayable if not already
    for i in sel:
        for attr in pm.listAttr(userDefined=True):
            pm.setAttr(i+'.'+attr, keyable=True)

def zero_out(self):

    # Set all the main transformations back to their default values
    trans = ['tx', 'ty', 'tz']
    rots = ['rx', 'ry', 'rz']
    scales = ['sx', 'sy', 'sz']

    for i in pm.ls(sl=True):
        for i in trans, rots:
            pm.setAttr(pm.ls(sl=True)[0]+'.'+i, 0)
        for i in scales:
            pm.setAttr(pm.ls(sl=True)[0]+'.'+i, 1)
    pm.setAttr(pm.ls(sl=True)[0]+'.visibility', 1)

def move_attr_up(self):

    obj = cmds.channelBox('mainChannelBox',q=True,mol=True)
    if obj:
        attr = cmds.channelBox('mainChannelBox',q=True,sma=True)
        if attr:
            for eachObj in obj:
                udAttr = cmds.listAttr(eachObj,ud=True)
                if not attr[0] in udAttr:
                    sys.exit('selected attribute is static and cannot be shifted')
                #temp unlock all user defined attributes
                attrLock = cmds.listAttr(eachObj,ud=True,l=True)
                if attrLock:
                    for alck in attrLock:
                        cmds.setAttr(eachObj + '.' + alck,lock=0)
                #shift up 
                for i in attr:
                    attrLs = cmds.listAttr(eachObj,ud=True)
                    attrSize = len(attrLs)
                    attrPos = attrLs.index(i)
                    if attrLs[attrPos-1]:
                        cmds.deleteAttr(eachObj,at=attrLs[attrPos-1])
                        cmds.undo()
                    for x in range(attrPos+1,attrSize,1):
                        cmds.deleteAttr(eachObj,at=attrLs[x])
                        cmds.undo()
                #relock all user defined attributes            
                if attrLock:
                    for alck in attrLock:
                        cmds.setAttr(eachObj + '.' + alck,lock=1)

def move_attr_down(self):

    obj = cmds.channelBox('mainChannelBox',q=True,mol=True)
    if obj:
        attr = cmds.channelBox('mainChannelBox',q=True,sma=True)
        if attr:
            for eachObj in obj:
                udAttr = cmds.listAttr(eachObj,ud=True)
                if not attr[0] in udAttr:
                    sys.exit('selected attribute is static and cannot be shifted')
                #temp unlock all user defined attributes
                attrLock = cmds.listAttr(eachObj,ud=True,l=True)
                if attrLock:
                    for alck in attrLock:
                        cmds.setAttr(eachObj + '.' + alck,lock=0)
                #shift down
                if len(attr) > 1:
                    attr.reverse()
                    sort = attr
                if len(attr) == 1:
                    sort = attr 
                for i in sort:
                    attrLs = cmds.listAttr(eachObj,ud=True)
                    attrSize = len(attrLs)
                    attrPos = attrLs.index(i)
                    cmds.deleteAttr(eachObj,at=attrLs[attrPos])
                    cmds.undo()
                    for x in range(attrPos+2,attrSize,1):
                        cmds.deleteAttr(eachObj,at=attrLs[x])
                        cmds.undo()
                #relock all user defined attributes            
                if attrLock:
                    for alck in attrLock:
                        cmds.setAttr(eachObj + '.' + alck,lock=1)

'''
/////////////// UTILITIES ///////////////
'''
def create_deformer():
    pass

def paint_deformer():
    pass

def mocap_group(self):

    for each in pm.ls(sl=True):
        dup = pm.duplicate(each , n = each.name().rpartition('_')[0]+'_CtrlMocap')
        pm.delete(pm.listRelatives(dup))
        pm.parent(each,dup)

        pm.setAttr(dup[0].rotateX, keyable=True, cb=True, lock=False)
        pm.setAttr(dup[0].rotateX, keyable=True)
        pm.setAttr(dup[0].rotateY, keyable=True, cb=True,lock=False)
        pm.setAttr(dup[0].rotateY, keyable=True)
        pm.setAttr(dup[0].rotateZ, keyable=True, cb=True,lock=False)
        pm.setAttr(dup[0].rotateZ, keyable=True)

        pm.setAttr(dup[0].translateX, keyable=True, cb=True,lock=False)
        pm.setAttr(dup[0].translateX, keyable=True)
        pm.setAttr(dup[0].translateY, keyable=True, cb=True,lock=False)
        pm.setAttr(dup[0].translateY, keyable=True)
        pm.setAttr(dup[0].translateZ, keyable=True, cb=True,lock=False)
        pm.setAttr(dup[0].translateZ, keyable=True)

def bake_mocap(slef):
    import bakeToSkel_UI
    reload(bakeToSkel_UI)

def sculpt_geo(self):

    mel.eval('SculptGeometryTool')

def curve_path(self):

    # Curve Dictionary Layout: {Object:{Curve:{Velocity_Per_Frame:Point_List}}}
    selected = pm.selected()
    curve_dict = {}

    # Create a locator for xform information
    for sel in selected:
        loc = pm.spaceLocator()
        pm.parentConstraint(sel, loc)
        vel_pos_dict = {}
        pos_list = []
        vel_list = []
        first_frame = pm.playbackOptions(min=True, q=True)
        last_frame = pm.playbackOptions(max=True, q=True)
        current_frame = pm.currentTime(first_frame)

        # Create a curve for editing
        curve_path = pm.curve(p=(0,0,0), name=sel+'_CrvPath')
        while current_frame != last_frame:

            # Get the position and calculate the velocity from distance over time
            current_frame = pm.currentTime(current_frame+1)
            pos = pm.xform(loc, t=True, q=True)
            pos_list.append(pos)
            curve_path = pm.curve(curve_path, r=True, p=pos_list)
            distance = pm.arclen(curve_path)
            velocity = distance/(last_frame - first_frame)
            vel_list.append(velocity)

            # Update the dictionary with all the values caluclated
            for vel in vel_list:
                vel_pos_dict.update({vel:pos_list[vel_list.index(vel)]})
            curve_dict.update({sel:{curve_path:vel_pos_dict}})
        pm.delete(loc)
    return curve_dict

def loc_at_sel(self):
    
    for i in pm.ls(sl=True):
        loc = pm.spaceLocator(name=str(i)+'_Loc')
        pm.parentConstraint(i, loc)

def abc_export(self):

    # Get a save file path
    abcFile = pm.fileDialog2(fileFilter='.abc', dialogStyle=2)
    abcFile = abcFile[0]

    # Get all items required for the export job.
    selected = pm.ls(sl=True)[0]
    firstFrame = pm.playbackOptions(min=True, q=True)
    lastFrame = pm.playbackOptions(max=True, q=True)
    steps = pm.optionMenu('steps', value=True, q=True)

    # Exports out the geo's hierarchy
    pm.AbcExport(j="-fr "+str(firstFrame)+" "+str(lastFrame)+" -uv -step "+str(steps)+" -root "+str(selected)+" -sn -ef -f "+str(abcFile))

def abc_export_selected(self):

    # Get a save file path
    abcFile = pm.fileDialog2(fileFilter='.abc', dialogStyle=2)
    abcFile = abcFile[0]

    # Get all items required for the export job.
    selected = pm.ls(sl=True)
    firstFrame = pm.playbackOptions(min=True, q=True)
    lastFrame = pm.playbackOptions(max=True, q=True)
    steps = pm.optionMenu('steps', value=True, q=True)

    # Exports out the geo's hierarchy
    pm.AbcExport(j="-fr "+str(firstFrame)+" "+str(lastFrame)+" -uv -step "+str(steps)+" -root "+str(selected)+" -sn -ef -f "+str(abcFile)+" -sl "+str(selected))

def import_alembic(self):

    abcFile = pm.fileDialog2(fileMode=1)
    cmds.file(abcFile[0], i=True)

def create_rivet(self):
    mel.eval("Rivet")
