require("config")
require("module")
require("common")

--class 'EVR'(EventReceiver)
EVR=LUAclass(EventReceiver)
function EVR:__init()
end

config_gymnist_all={
	"../Resource/motion/gymnist/gymnist.wrl",
	'../Resource/motion/gymnist/gymnist.dof',
	{ 
		{'lfoot', vector3(0.000000,-0.053740,0.111624)},
		{'rfoot', vector3(0.000000,-0.054795,0.112272)},
		{ 'lhand', vector3(0.000000,-0.053740,0.111624), },
		{ 'rhand', vector3(0.000000,-0.054795,0.112272), },
	},
	skinScale=100,
	initialHeight=0.07,
	frameRate=120,
}
config=config_gymnist_all
--config=config_run


require('subRoutines/VelocityFields')

function ctor()
	
	mEventReceiver=EVR()
	this:updateLayout();

	mLoader=MainLib.VRMLloader (config[1])
	mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo, config[2])

	if config.frameRate==120 then
		mMotionDOFcontainer:resample(mMotionDOFcontainer:copy(), 4)
	else 
		assert(config.frameRate==30)
	end

	config.frameRate=30
	mLoader.dofInfo:setFrameRate(30)

	mMotionDOF=mMotionDOFcontainer.mot

	-- in meter scale
	for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i, 1, mMotionDOF:matView()(i,1)+(config.initialHeight or 0))
	end

	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, false);
	mSkin2= RE.createVRMLskin(mLoader, false);
	local s=config.skinScale
	mSkin:scale(s,s,s); -- motion data often is in meter unit while visualization uses cm unit.
	mSkin2:scale(s,s,s);
	mSkin2:setTranslation(100,0,0);
	mSkin2:setMaterial('lightgrey_transparent')

	mSkin:applyMotionDOF(mMotionDOF)
	RE.motionPanel():motionWin():addSkin(mSkin)

	local filterSize=11 -- has to be an odd number
	mFilter=OnlineFilter(mLoader, mMotionDOF:row(0), filterSize)

end

function onCallback(w, userData)  
end

function dtor()
end

function frameMove(fElapsedTime)
end

function EVR:onFrameChanged(win, iframe)
	if noOnframeChanged then return end
	self.prevFrame=self.currFrame
	self.currFrame=iframe
	local i=iframe
	local pose=mMotionDOF:row(i)

	if self.prevFrame then

		print(i)
		mFilter:setCurrPose(pose)

		mSkin2:setPoseDOF(mFilter:getFiltered())
	end
end
function handleRendererEvent(ev)
	return 0
end
