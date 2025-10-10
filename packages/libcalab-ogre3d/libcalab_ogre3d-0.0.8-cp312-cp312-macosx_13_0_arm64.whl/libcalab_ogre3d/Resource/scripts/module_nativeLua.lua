
require('mylib')
-- create dummy classes before loading 'module.lua' 
RE={}
function  RE.ogreSceneManager() end
util.BinaryFile={}
util.Timer=LUAclass()
function util.Timer:__init(...) end
Ogre={}
Ogre.ObjectList={}
Ogre.SceneNode={}
sop={}
Motion={}
MotionDOFinfo={}
MainLib={}
Fltk={}
MotionDOFview={}
Liegroup={}
Liegroup.se3={}
Liegroup.dse3={}
Liegroup.Inertia={}
Viewpoint={}
FlLayout={}
EVR={}
MotionUtil={}
MotionUtil.FullbodyIK_MotionDOF={}
MainLib.VRMLloader={}
matrix3={}
matrix4={}
TStrings={}
MotionLoader={}
Bone={}
vector3=LUAclass()
function vector3:__init(...) end
function vector3.__add(a,b) return vector3() end
function vector3.__sub(a,b) return vector3() end
function vector3.__mul(a,b) return vector3() end
quater=LUAclass()
function quater:__init(...) end
function quater.__mul(a,b) return quater() end
transf=LUAclass()
function transf:__init(...) end
vectorn={}
intvectorn={}
boolN={}
intIntervals={}
vector4={}
Mesh={}
Geometry={}
Physics={}
Physics.DynamicsSimulator={}
Physics.DynamicsSimulator_TRL_QP={}
Physics.DynamicsSimulator_TRL_LCP={}
Physics.DynamicsSimulator_Trbdl_penalty={}
QuadraticFunctionHardCon={}
HessianQuadratic={}
Physics.ContactBasis={}
Physics.Vec_ContactBasis={}
matrixn={}
MotionDOF={}
intmatrixn={}
matrixnView={}
hypermatrixn={}
vector3N={}
quaterN={}
vector2={}
Pose={}
boolNView={}
require('module')

