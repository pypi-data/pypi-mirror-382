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

	do

		mMotion=Motion(mMotionDOF)
		local self={loader_euler=mLoader, motionDOF_euler=mMotionDOF, DMotionDOF_euler=mMotionDOF:calcDerivative(30) }

		-- important!!!
		-- convert loader, motionDOF, and its time-derivative to new formats.

		self.loader=self.loader_euler:copy()
		self.loader:changeAll3DOFjointsToSpherical()
		for i=1, self.loader:numBone()-1 do
			print(self.loader:VRMLbone(i):numHRPjoints())
		end
		self.loader:printHierarchy()

		local nf=self.motionDOF_euler:numFrames()
		self.motQ=matrixn(nf, self.loader.dofInfo:numDOF())
		self.motDQ=matrixn(nf, self.loader.dofInfo:numActualDOF())

		local tree=MotionUtil.LoaderToTree(self.loader_euler, false,false)

		local euler_dofInfo=self.loader_euler.dofInfo
		local spherical_dofInfo=self.loader.dofInfo

		for i=0, nf-1 do
			tree:setPoseDOF(euler_dofInfo, self.motionDOF_euler:row(i))
			tree:setVelocity(euler_dofInfo, self.DMotionDOF_euler:row(i))

			tree:getSphericalState(spherical_dofInfo, self.motQ:row(i), self.motDQ:row(i))
		end
		mMot=self
		mLoader=mMot.loader
		mMotionDOF=nil
		mMotionDOFcontainer=nil

		mMotionDOF=MotionDOF(mLoader.dofInfo)
		mMotionDOF:set(mMotion)
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

	--mDeriv=VelocityFields(mLoader, mMotionDOFcontainer, mMotionDOF:row(0), {frameRate=config.frameRate, alignRoot=true}) 
	mIntegrator=MotionUtil.LoaderToTree(mLoader, false, false)
	g_prevFrame=0
	mCurrQ=mMot.motQ:row(0):copy()


	this:create("Button", "reset to currFrame", "reset to currFrame")
	this:updateLayout()
end

function onCallback(w, userData)  
	if w:id()=="reset to currFrame" then
		mDeriv.pose=mMotionDOF:row(mEventReceiver.GUIcurrFrame)
		g_prevFrame=mEventReceiver.GUIcurrFrame
		mSkin2:setPoseDOF(mDeriv.pose)
	end
end

function dtor()
end

function frameMove(fElapsedTime)
end

function EVR:onFrameChanged(win, iframe)
	if noOnframeChanged then return end
	self.GUIcurrFrame=iframe -- not used
	local i=iframe

	if g_prevFrame and g_prevFrame<mMot.motQ:rows() then

		local ref_dq=mMot.motDQ:row(i)

		local dofInfo=mLoader.dofInfo
		mIntegrator:setSphericalState(dofInfo, mCurrQ, ref_dq)
		mIntegrator:integrate(dofInfo, 1/config.frameRate)
		mIntegrator:getSphericalQ(dofInfo, mCurrQ)


		--local pose=vectorn()
		--mIntegrator:getPoseDOF(dofInfo, pose)
		--mSkin2:setPoseDOF(pose)

		-- 이게 더 빠름.
		mSkin2:setSamePose(mIntegrator)

		g_prevFrame=g_prevFrame+1
	end
end
function handleRendererEvent(ev)
	return 0
end
