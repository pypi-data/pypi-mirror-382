require("config")
require("module")
require("common")
require("RigidBodyWin/subRoutines/Constraints")


config_hyunwoo={
	"../Resource/motion/locomotion_hyunwoo/hyunwoo_lowdof_T.wrl",
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
function createIKsolver(solverType, loader, config)
	local out={}
	local mEffectors=MotionUtil.Effectors()
	local numCon=#config
	mEffectors:resize(numCon);
	out.effectors=mEffectors
	out.numCon=numCon

	for i=0, numCon-1 do
		local conInfo=config[i+1]
		local kneeInfo=1
		local lknee=loader:getBoneByName(conInfo[kneeInfo])
		mEffectors(i):init(loader:getBoneByName(conInfo[kneeInfo+1]), conInfo[kneeInfo+2])
	end
	g_con=MotionUtil.Constraints() -- std::vector<MotionUtil::RelativeConstraint>
	out.solver=MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_lbfgs(loader.dofInfo);
	return out
end

function loadMotion(skel, motion, skinScale)
	local mot={}
	mot.loader=MainLib.VRMLloader (skel)
	mot.motionDOFcontainer=MotionDOFcontainer(mot.loader.dofInfo, motion)
	if skinScale then
		mot.skin=createSkin(skel, mot.loader, skinScale)
		mot.skin:applyMotionDOF(mot.motionDOFcontainer.mot)
		mot.skin:setMaterial('lightgrey_transparent')
	end
	return mot
end

function ctor()
	this:create("Button", "rotate light", "rotate light",1)
	this:create("Value_Slider", "arm ori y", "arm ori y",1)
	this:widget(0):sliderRange(-math.rad(90),math.rad(90))
	this:widget(0):sliderValue(0)
	

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


	mMotionDOFcontainer=mMot.motionDOFcontainer
	mMotionDOF=mMotionDOFcontainer.mot

	-- in meter scale
	for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i, 1, mMotionDOF:matView()(i,1)+(config.initialHeight or 0))
	end



	mLoader:setPoseDOF(mMotionDOF:row(0))
	mPose0=mLoader:getPoseMap()

	if true then
		local loader=mLoader
		-- add translation joints (y)
		local bone=loader:getBoneByName('RightKnee')
		bone=MainLib.VRMLloader.upcast(bone)
		
		if true then
			-- 같은 본(같은 treeIndex)에 translation joint꾸겨 넣기
			local trans=bone:getTranslationalChannels()
			local rot=bone:getRotationalChannels()

			trans="Y"
			loader:setChannels(bone, trans, rot)
		else
			-- 차일드 조인트와 본 추가하기.
			loader:insertChildJoint(bone, "Y", "", 'RightKnee_trans', true)
		end

		loader:printHierarchy()
	end
	mPose=vectorn()
	

	mLoader:setPoseMap(mPose0)
	mLoader:getPoseDOF(mPose)

	if false then
		local dofInfo=mLoader.dofInfo
		local bi=mLoader:getTreeIndexByName('RightKnee')
		local ti=dofInfo:startT(bi)
		local ri=dofInfo:startR(bi)
		dbg.console()
	end
	
	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, true);
	mSkin:setMaterial("lightgrey_transparent")
	local s=config.skinScale
	mSkin:scale(s,s,s); -- motion data often is in meter unit while visualization uses cm unit.
	mSkin:setThickness(3/s)
	mSkin:setPoseDOF(mPose);


	mSolverInfo=createIKsolver(solver, mLoader, config[3])
	mEffectors=mSolverInfo.effectors
	numCon=mSolverInfo.numCon
	mIK=mSolverInfo.solver

	footPos=vector3N (numCon);

	mLoader:setPoseDOF(mPose)
	local originalPos={}
	for i=0,numCon-1 do
		local opos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		originalPos[i+1]=opos*config.skinScale
	end
	table.insert(originalPos, mLoader:bone(1):getFrame().translation*config.skinScale) -- desired COM initially unused.
	mCON=Constraints(unpack(originalPos))
	--mCON:setOption(1*config.skinScale)
	mCON:connect(eventFunction)
end
function limbik()
	mLoader:setPoseMap(mPose0)
	mLoader:getPoseDOF(mPose)
	local hasCOM=0
	local hasRot=1
	local hasMM=0
	local COM=mCON.conPos(2)/config.skinScale
	mIK:_changeNumEffectors(numCon)
	mIK:_changeNumConstraints(hasCOM+hasRot+hasMM)
	-- local pos to global pos
	for i=0,numCon-1 do
		mIK:_setEffector(i, mEffectors(i).bone, mEffectors(i).localpos)

		local originalPos=mCON.conPos(i)/config.skinScale
		footPos(i):assign(originalPos);
	end
	
	if hasCOM==1 then
		mIK:_setCOMConstraint(0, COM)
	end
	if hasRot==1 then
		local bone=mLoader:getBoneByName('LeftElbow')

		mIK:_setOrientationConstraint(hasCOM, bone, quater(this:findWidget('arm ori y'):sliderValue(), vector3(0,1,0)));
	end
	if hasMM==1 then
		mIK:_setMomentumConstraint(hasCOM+hasRot, vector3(0,0,0), vector3(0,0,0));
	end
	mIK:_effectorUpdated()

	mIK:IKsolve(mPose, footPos)
	if true then

		local dofInfo=mLoader.dofInfo
		local ibone=mLoader:getTreeIndexByName('RightKnee')
		local qi0=dofInfo:startT(ibone) --0
		print(mPose(qi0))
	end
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
	end
	limbik()
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
