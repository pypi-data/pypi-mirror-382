arg={...}
require("config")
require("module")
require("moduleIK")
require("common")
require("retargetting/module/poseDeformer")
require("retargetting/module/constraintMarkingModule")
require("retargetting/module/displacementMapModule")


config={
	--{
	--	skel="../Samples/scripts/RigidBodyWin/retargetting/data/Data/2_1.bvh",
	--	skinScale=1.05,
	--},
	--{
	--	--skel="../Resource/motion/KIST/rigging_model_bvh.bvh",
	--	--skinScale=100,
	--	skel="../Resource/jae/human/humanHanyang.wrl",
	--	motion="../Resource/jae/human/humanHanyang.dof",
	--	skinScale=100,
	--},
	{
		skel="../Resource/mocap_manipulation/bvh_files/2/2_skel_glove_forHandIK_reduced.wrl",
		motion='../Resource/mocap_manipulation/bvh_files/2/2_skel_glove_forHandIK_reduced.dof',
		skinScale=1,
	},
	--{
	--	skel="../Samples/scripts/RigidBodyWin/retargetting/data/Data/2_1.bvh.dof.bvh",
	--	skinScale=2.54,
	--},
	--{
	--	skel="../Samples/scripts/RigidBodyWin/retargetting/data/Data/2_2.bvh.dof.bvh",
	--	skinScale=2.54,
	--},
	--{
	--	skel="../Samples/scripts/RigidBodyWin/retargetting/data/Data/2_4.bvh.dof.bvh",
	--	skinScale=2.54,
	--},
	--{
	--	skel="../Samples/scripts/RigidBodyWin/retargetting/data/Data/2_5.bvh.dof.bvh",
	--	skinScale=2.54,
	--},
	--{
	--	skel="../Samples/scripts/RigidBodyWin/retargetting/data/ETRI_Template_Skeleton/fitting.asf",
	--	motion="../Samples/scripts/RigidBodyWin/retargetting/data/ETRI_Template_Skeleton/fitting.amc",
	--	skinScale=2.54,
	--},
	--{
	--	skel="../Resource/motion/skeletonEditor/fitting2_1dof_fixed.wrl",
	--	motion="../Resource/motion/skeletonEditor/fitting2_1dof_fixed.wrl.dof",
	--	skinScale=2.54,
	--}
}

function ctor()
	mEventReceiver=EVR()

	this:create("Button","goto I", "goto I")
	this:updateLayout()
	this:redraw()

	mObjectList=Ogre.ObjectList()

	mMot={}
	local translation=100-#config/2
	for i,v in ipairs(config) do
		if os.isFileExist(v.skel) then
		mMot[i]=loadMotion(v.skel, v.motion, v.skinScale)
		local motion=mMot[i].motionDOFcontainer.mot
		local roottf=MotionDOF.rootTransformation(motion:row(0))
		local T=roottf.translation:copy()
		T.y=0
		motion:transform(transf(quater(1,0,0,0), -T))
		mMot[i].skin:setTranslation(translation, 0,0)
		mMot[i].motion=Motion(motion)
		mMot[i].skinAxes=RE.createSkin(mMot[i].motion, PLDPrimSkin.POINT)
		mMot[i].skinAxes:setTranslation(translation, 0,0)
		mMot[i].skinAxes:setScale(v.skinScale, v.skinScale, v.skinScale)
		RE.motionPanel():motionWin():addSkin(mMot[i].skin)
		RE.motionPanel():motionWin():addSkin(mMot[i].skinAxes)
		translation=translation+100
	end
	end
end

function onCallback(w, userData)
	if w:id()=="goto I" then
		for i,v in ipairs(config) do
			mMot[i].loader:updateInitialBone()
			local pose=vectorn()
			mMot[i].loader:getPoseDOF(pose)
			mMot[i].skin:setPoseDOF(pose)
		end
	end
end

function dtor()
	dbg.finalize()
	detachSkins()
end

if EventReceiver then
	--class 'EVR'(EventReceiver)
	EVR=LUAclass(EventReceiver)
	function EVR:__init(graph)
		--EventReceiver.__init(self)
		self.currFrame=0
		self.cameraInfo={}
	end
end

function EVR:onFrameChanged(win, iframe)
	if noEvent then return end
	self.currFrame=iframe
end


function frameMove(fElapsedTime)
end

function detachSkins()
	if RE.motionPanelValid() then
		for i, v in ipairs(mMot) do
			RE.motionPanel():motionWin():detachSkin(v.skin)
		end
	end
	-- remove objects that are owned by LUA
	collectgarbage()
end

function renderOneFrame()
	noEvent=true
	RE.renderOneFrame(false)
	noEvent=false
end
function handleRendererEvent()
	return 0
end
