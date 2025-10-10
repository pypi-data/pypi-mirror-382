require("config")
require("module")
require("common")
require("RigidBodyWin/subRoutines/Constraints")

-- moduleIk.lua contains the actual contructors of the IK solvers.
require("moduleIK")

config_hyunwoo={
	"../Resource/motion/locomotion_hyunwoo/hyunwoo_lowdof_T2.wrl",
	"../Resource/motion/locomotion_hyunwoo/hyunwoo_lowdof_T_locomotion_hl.dof",
	{
		{'LeftKnee', 'LeftAnkle', vector3(0, -0.06, 0.08), reversed=false},
		{'RightKnee', 'RightAnkle', vector3(0, -0.06, 0.08), reversed=false},
	},
	skinScale=100,
}

config=config_hyunwoo

function eventFunction()
	limbik()
end

HybridIK=LUAclass()

function HybridIK:__init(loader, config) 
	local eff=MotionUtil.Effectors()
	local numCon=#config
	eff:resize(numCon);
	local _hipIndex=intvectorn() -- used only when the config contains shoulder joints, e.g. {'lshoulder', 'lradius', 'lhand', vector3(0,0,0), reversed=true},
	local kneeIndex=intvectorn(numCon)
	local axis=vectorn(numCon)
	self.effectors=eff
	self.numCon=numCon
	self.kneeIndex=kneeIndex
	self._hipIndex=_hipIndex
	self.axis=axis

	for i=0, numCon-1 do
		local conInfo=config[i+1]
		local kneeInfo=1
		if #conInfo==4 then
			_hipIndex:resize(numCon)
			local lhip=loader:getBoneByName(conInfo[1])
			_hipIndex:set(i, lhip:treeIndex())
			kneeInfo=2
		end
		local lknee=loader:getBoneByName(conInfo[kneeInfo])
		eff(i):init(loader:getBoneByName(conInfo[kneeInfo+1]), conInfo[kneeInfo+2])
		kneeIndex:set(i, lknee:treeIndex())
		if conInfo.reversed then
			axis:set(i,-1)
		else
			axis:set(i,1)
		end
	end

	self.loader=loader
	self.loader_slide=loader:copy()

	do
		local loader=self.loader_slide
		-- add translation joints (y)
		for i=0, numCon-1 do
			local bone=loader:getBoneByName(config[i+1][1])
			bone=MainLib.VRMLloader.upcast(bone)

			if true then
				-- 같은 본(같은 treeIndex)에 translation joint꾸겨 넣기
				local trans=bone:getTranslationalChannels()
				local rot=bone:getRotationalChannels()

				trans="Y"
				loader:setChannels(bone, trans, '')
			end
		end
		loader:printHierarchy()

		if false then
			self.debugSkin= RE.createVRMLskin(loader, true);
			self.debugSkin:setMaterial("lightgrey_transparent")
			local s=100
			self.debugSkin:scale(s,s,s); -- motion data often is in meter unit while visualization uses cm unit.
		end
	end

	self.hips=intvectorn(numCon)
	self.ankles=intvectorn(numCon)
	self.knees=intvectorn(numCon)
	self.legLen=vectorn(numCon)
	for i=0, numCon-1 do
		self.hips:set(i, loader:getBoneByName(config[i+1][1]):parent():treeIndex())
		self.knees:set(i, loader:getBoneByName(config[i+1][1]):treeIndex())
		self.ankles:set(i, loader:getBoneByName(config[i+1][2]):treeIndex())
		self.legLen:set(i, loader:bone(self.knees(i)):getOffset():length()+loader:bone(self.ankles(i)):getOffset():length())
	end

	assert(loader.dofInfo:numDOF()==self.loader_slide.dofInfo:numDOF())

	do
		-- compatibility between the two loaders
		local isCompatible=boolN(loader.dofInfo:numDOF())
		isCompatible:setAllValue(true)

		local isAnkle=boolN(loader.dofInfo:numDOF())
		isAnkle:setAllValue(false)

		for i=0, numCon-1 do
			isCompatible:range(loader.dofInfo:startR(self.hips(i)), loader.dofInfo:endR(self.ankles(i))):setAllValue(false)
			isAnkle:range(loader.dofInfo:startR(self.ankles(i)), loader.dofInfo:endR(self.ankles(i))):setAllValue(true)
		end
		self.compatibleDOFs=intvectorn()
		self.compatibleDOFs:findIndex(isCompatible, true)
		self.ankleDOFs=intvectorn()
		self.ankleDOFs:findIndex(isAnkle, true)
	end

	-- three step solve.
	self.solver1=MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_lbfgs(self.loader_slide.dofInfo);
	self.solver2=LimbIKsolver(loader.dofInfo,eff, kneeIndex, axis)
	self.solver3=MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_lbfgs(self.loader.dofInfo);
end
function HybridIK:IKsolve(mPose, footpos, COM, rootposweight)


	gTimer=util.PerfTimer2()
	gTimer:start()
	local mLoader=self.loader
	local mEffectors=self.effectors
	mLoader:setPoseDOF(mPose);

	local delta=COM-mLoader:calcCOM()
	if delta.y>0 then
		delta.y=0
	end
	mPose:setVec3(0,mPose:toVector3(0)+delta*rootposweight)

	self.loader_slide:setPoseDOF(mPose)

	local pose_slide=vectorn()
	do 
		-- set loader_slide, pose_slide
		local loader=self.loader
		local ls=self.loader_slide
		local numCon=self.numCon
		local currLegLen=vectorn(numCon)
		for i=0, numCon-1 do
			local hips=self.hips
			local knees=self.knees
			local ankles=self.ankles
			local q=loader:bone(hips(i)):getFrame().rotation
			local axis1=loader:bone(ankles(i)):getFrame().translation-loader:bone(hips(i)):getFrame().translation
			local axis2=loader:bone(knees(i)):getFrame().translation-loader:bone(hips(i)):getFrame().translation
			currLegLen:set(i, axis1:length())

			local q2=quater()
			q2:axisToAxis(axis2, axis1)

			--g= p_g*local
			---> local=p_g:inverse()*g
			ls:bone(hips(i)):getLocalFrame().rotation:assign(ls:bone(1):getFrame().rotation:inverse()*(q2*q))

		end
		ls:fkSolver():getPoseDOFfromLocal(pose_slide)

		-- set legLen
		for i=0, numCon-1 do
			local t=ls.dofInfo:startT(self.knees(i))
			pose_slide:set(t, self.legLen(i)-currLegLen(i))
		end


		if false and self.debugSkin then
			local p1=vectorn()
			self.debugSkin:setPoseDOF(pose_slide)
		end
	end

	if true then
		-- solve slide ik
		local mIK=self.solver1
		local hasCOM=0
		--if COM then hasCOM=1 end
		mIK:_changeNumEffectors(numCon)
		mIK:_changeNumConstraints(hasCOM)
		-- local pos to global pos
		for i=0,numCon-1 do
			mIK:_setEffector(i, mEffectors(i).bone, mEffectors(i).localpos)
		end

		if hasCOM==1 then
			mIK:_setCOMConstraint(0, COM,1,0.1,1)
		end
		mIK:_effectorUpdated()
		mIK:setParam('slide_damping_weight', 0.1, 0.00001)
		mIK:IKsolve(pose_slide, footPos)
		if true and self.debugSkin then
			local p1=vectorn()
			self.debugSkin:setPoseDOF(pose_slide)
		end
	end

	local origAnkleDOFs=mPose:extract(self.ankleDOFs)
	mPose:assignSelective(self.compatibleDOFs, pose_slide:extract(self.compatibleDOFs))


	local footOri=quaterN(numCon)
	for i=0,numCon-1 do
		footOri(i):assign(mEffectors(i).bone:getFrame().rotation)
	end

	local importance=CT.ones(numCon)
	self.solver2:IKsolve3(mPose, MotionDOF.rootTransformation(mPose), footPos, footOri, importance)
	mPose:assignSelective(self.ankleDOFs, origAnkleDOFs)

	if true then
		-- solve final ik
		local mIK=self.solver3
		local hasCOM=0
		if COM then hasCOM=1 end
		mIK:_changeNumEffectors(numCon)
		mIK:_changeNumConstraints(hasCOM)
		-- local pos to global pos
		for i=0,numCon-1 do
			mIK:_setEffector(i, mEffectors(i).bone, mEffectors(i).localpos)
		end

		if hasCOM==1 then
			mIK:_setCOMConstraint(0, COM,1,0.1,1)
		end
		mIK:_effectorUpdated()
		mIK:IKsolve(mPose, footPos)
	end

	RE.output2('part12', gTimer:stop())
end

function ctor()
	this:create("Button", "rotate light", "rotate light",1)
	

	this:create("Check_Button", "use knee damping", "use knee damping")
	this:widget(0):checkButtonValue(true)
	this:create("Value_Slider", "rootposweight", "rootposweight")
	this:widget(0):sliderValue(1.0)
	
	this:updateLayout();

	--dbg.console();
	mMot=loadMotion(config[1], config[2])
	mLoader=mMot.loader

	--local max_iter=mLoader:numBone()
	for i=1, mLoader:numBone()-1 do
		if mLoader:VRMLbone(i):numChannels()==0 then
			mLoader:removeAllRedundantBones()
			--mLoader:removeBone(mLoader:VRMLbone(i))
			--mLoader:export(config[1]..'_removed_fixed.wrl')
			break
		end
	end
	mLoader:_initDOFinfo()

	if true then
		-- convert ankle joints to 3DOFs (YZX)

		local srcMotion=Motion( mMot.motionDOFcontainer.mot)
				
		-- ankle L and R
		mLoader:setChannels(mLoader:getBoneByName(config[3][1][2]), '', 'YZX')
		mLoader:setChannels(mLoader:getBoneByName(config[3][2][2]), '', 'YZX')

		mMot.motionDOFcontainer=nil -- no longer valid
		mMotionDOF=MotionDOF(mLoader.dofInfo)
		mMotionDOF:set(srcMotion)
	else
		mMotionDOF=mMot.motionDOFcontainer.mot
	end

	-- in meter scale
	for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i, 1, mMotionDOF:matView()(i,1)+(config.initialHeight or 0))
	end

	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, true);
	mSkin:setMaterial("lightgrey_transparent")
	local s=config.skinScale
	mSkin:scale(s,s,s); -- motion data often is in meter unit while visualization uses cm unit.
	mSkin:setThickness(3/s)
	mPose=vectorn()
	mPose:assign(mMotionDOF:row(0));
	mSkin:setPoseDOF(mPose);


	mSolverInfo=HybridIK(mLoader, config[3])
	mEffectors=mSolverInfo.effectors
	numCon=mSolverInfo.numCon

	footPos=vector3N (numCon);

	mLoader:setPoseDOF(mPose)
	local originalPos={}
	for i=0,numCon-1 do
		local opos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		originalPos[i+1]=opos*config.skinScale
	end
	table.insert(originalPos, mLoader:calcCOM()*config.skinScale)
	mCON=Constraints(unpack(originalPos))
	--mCON:setOption(1*config.skinScale)
	mCON:connect(eventFunction)
end
function limbik()
	mPose:assign(mMotionDOF:row(0));

	for i=0,numCon-1 do
		local originalPos=mCON.conPos(i)/config.skinScale
		footPos(i):assign(originalPos);
	end
	local COM=mCON.conPos(numCon)/config.skinScale

	mSolverInfo:IKsolve(mPose, footPos, COM, this:findWidget('rootposweight'):sliderValue())
	mSkin:setPoseDOF(mPose);
end

function onCallback(w, userData)  

	if w:id()=="button1" then
		print("button1\n");
	elseif w:id()=='rotate light' then
		local osm=RE.ogreSceneManager()
		if osm:hasSceneNode("LightNode") then
			local lightnode=osm:getSceneNode("LightNode")
			lightnode:rotate(quater(math.rad(30), vector3(0,1,0)))
		end
	else
		limbik()
	end
end

function dtor()
end

function frameMove(fElapsedTime)
end

function handleRendererEvent(ev, button, x,y) 
	if mCON then
		return mCON:handleRendererEvent(ev, button, x,y)
	end
	return 0
end
