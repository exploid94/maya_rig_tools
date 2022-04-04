'''
Charles' skinMerge scripts
'''

import pymel.core as pm
import maya.cmds as cmds
from maya.api import OpenMaya as om2
from maya.api import OpenMayaAnim as oma2
import re

# Select mesh w/ skincluster to be transferred (face geo) then select destination mesh for stacked skincluster (body)			
# Charles' skinMerge.py script
class skin_merge():
    ## ======================================================================
    def get_deform_shape(self, ob):
        """
        Gets the visible geometry shape regardless of whether or not
        the object is deformed or not.
        :param ob: The object to check.
        :returns: The object's deform shape.
        """
    
        ob = pm.PyNode(ob)
        if ob.type() in ['nurbsSurface', 'mesh', 'nurbsCurve']:
            ob = ob.getParent()
        shapes = pm.PyNode(ob).getShapes()
        if len(shapes) == 1:
            return( shapes[0] )
        else:
            real_shapes = [ x for x in shapes if not x.intermediateObject.get() ]
        return( real_shapes[0] if len(real_shapes) else None )
    
    
    ## ---------------------------------------------------------------------
    def get_skin_cluster(self, ob):
        """
        Find the first skinCluster on the object that actually effects it.
        When multiple deformers are layered, this means that the latest skin
        in the deform chain will be returned.
        In situations where multiple skins are layered through blendshapes,
        this function will only return the skin on the current mesh and not
        any of the blendshape sources.
        :param ob: The object whose skin you wish to return.
        :returns: A skinCluster object, or None.
        """
    
        shape = self.get_deform_shape(ob)
        if shape is None:
            return(None)
        skins = pm.ls( pm.listHistory( shape ), type='skinCluster' )
        if len( skins ):
            for skin in skins:
                # log( '\t+ Processing %s...' % skin )
                groupId = skin.input[0].groupId.inputs( plugs=True )[0]
                outputs = groupId.outputs(plugs=True)
                for outp in outputs:
                    node = outp.node()
                    if node == shape or node == ob:
                        ## force neighbors!
                        skin.weightDistribution.set(1) ## neighbors
                        return( skin )
        return( None )
    
    
    ## ---------------------------------------------------------------------
    def log(self, msg, warn=False, error=False ):
        if warn and error:
            raise ValueError('Please specify only one of warn / error.')
    
        log_func = om2.MGlobal.displayInfo
        if warn:
            log_func = om2.MGlobal.displayWarning
        elif error:
            log_func = om2.MGlobal.displayError
    
        log_func( msg )
    
    
    ## ======================================================================
    ## om2 utilities
    def get_mobject(self, name ):
        sel = om2.MGlobal.getSelectionListByName( name )
        return sel.getDependNode(0)
    
    ## ---------------------------------------------------------------------
    def get_dag_path(self, name ):
        sel = om2.MGlobal.getSelectionListByName( name )
        return sel.getDagPath(0)
    
    ## ---------------------------------------------------------------------
    def get_mfn_skin(self, skin_ob ):
        if isinstance( skin_ob, pm.PyNode ):
            skin_ob = self.get_mobject( skin_ob.longName() )
        return oma2.MFnSkinCluster( skin_ob )
    
    ## ---------------------------------------------------------------------
    def get_mfn_mesh(self, mesh_ob ):
        if isinstance( mesh_ob, pm.PyNode ):
            mesh_ob = self.get_mobject( mesh_ob.longName() )
        return om2.MFnMesh( mesh_ob )
    
    ## ---------------------------------------------------------------------
    def get_complete_components(self, mesh_ob ):
        assert( isinstance(mesh_ob, om2.MFnMesh) )
        comp = om2.MFnSingleIndexedComponent()
        ob = comp.create( om2.MFn.kMeshVertComponent )
        comp.setCompleteData( mesh_ob.numVertices )
        return( ob )
    
    ## ======================================================================
    def move_skin(self, source, target ):
        source_shape = self.get_deform_shape( source )
        source_dp = self.get_dag_path( source_shape.longName() )
        source_skin = self.get_skin_cluster( source )
        source_mfn  = self.get_mfn_skin( source_skin )
        source_mesh = self.get_mfn_mesh( self.get_deform_shape(source) )
        components = self.get_complete_components( source_mesh )
    
        weights, influence_count = source_mfn.getWeights( source_dp, components )
    
        pm.select( cl=True )
        target_skin = pm.deformer( target, type='skinCluster', n='MERGED__' + source_skin.name() )[0]
    
        ## copy over input values / connections
        bind_inputs = [ (x.inputs(plugs=True)[0] if x.isConnected() else None) for x in source_skin.bindPreMatrix ]
        bind_values = [ x.get() for x in source_skin.bindPreMatrix ]
        mat_inputs  = [ (x.inputs(plugs=True)[0] if x.isConnected() else None) for x in source_skin.matrix ]
        mat_values  = [ x.get() for x in source_skin.matrix ]
    
        for index, bind_value, mat_value in zip( xrange(influence_count), bind_values, mat_values ):
            target_skin.bindPreMatrix[index].set( bind_value )
            target_skin.matrix[index].set( mat_value )
    
        for index, bind_input, mat_input in zip( xrange(influence_count), bind_inputs, mat_inputs ):
            if bind_input:
                bind_input >> target_skin.bindPreMatrix[index]
            if mat_input:
                mat_input >> target_skin.matrix[index]
    
        ## copy over weights
        target_mfn  = self.get_mfn_skin( target_skin )
        target_mesh = self.get_mfn_mesh( self.get_deform_shape(target) )
        target_dp   = self.get_dag_path( self.get_deform_shape(target).longName() )
        components  = self.get_complete_components( target_mesh )
        all_indices = om2.MIntArray( range(influence_count) )
    	
        target_mfn.setWeights( target_dp, components, all_indices, weights )