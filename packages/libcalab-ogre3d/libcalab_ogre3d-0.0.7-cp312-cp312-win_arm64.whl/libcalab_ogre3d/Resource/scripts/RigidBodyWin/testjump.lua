require("config")
require("module")
require("common")
require("RigidBodyWin/subRoutines/Constraints")
require("retargetting/module/constraintMarkingModule")

config={
    skel="../Resource/motion/justin_jump.wrl",
	motion='../Resource/motion/justin_jump.dof',
	conFile='../Resource/motion/justin_jump.dof.conEditor',
	con={
		{'ltibia', 'lfoot', vector3(0,0,0), reversed=false},
		{'rtibia', 'rfoot', vector3(0,0,0), reversed=false},
	},
	initialHeight=0,
	skinScale=100,
	currFrame=21000,
	range={21000, 21300},
	editCOMframe=21269,
}

function ctor()

	this:create("Button", "?","?")
	this:updateLayout()

	mEventReceiver=EVR()
    mLoader=MainLib.VRMLloader (config.skel)
	mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo, config.motion)
	mOriginalMotion=mMotionDOFcontainer.mot:copy()
	do
		local con=util.loadTable(config.conFile)
		config.constraints=con.targets
	end

	for k, v in pairs(config.constraints) do
		v.importance=conToImportance(v.con, 10)
		Imp.ChangeChartPrecision(70);
		local pSignalL=Imp.DrawChart(v.importance:row(), Imp.LINE_CHART, 0, 1);
		RE.motionPanel():scrollPanel():addPanel(pSignalL)
		RE.motionPanel():scrollPanel():setLabel(k)
	end
	mMotionDOF=mMotionDOFcontainer.mot
	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, false);
	mSkin:scale(config.skinScale,config.skinScale,config.skinScale); -- motion data is in meter unit while visualization uses cm unit.
	mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
	RE.motionPanel():motionWin():addSkin(mSkin)
	RE.motionPanel():motionWin():changeCurrFrame(config.currFrame)

	mLoader:setPoseDOF(mMotionDOFcontainer.mot:row(config.editCOMframe))
	mCOM=mLoader:calcCOM()
	
	mEditConstraints=Constraints({mCOM*config.skinScale})
	mEditConstraints:connect(eventFunction)


	mComTraj=calcCOMtraj()
	dbg.draw('Traj', mComTraj:matView()*config.skinScale, 'COMtraj')

	do
		-- create IKsolver
		mIKsolver={}
		mIKsolver.effectors=MotionUtil.Effectors()
		local con=config.con
		local kneeIndices=intvectorn()
		local axisSign=vectorn()

		mIKsolver.footPos=vector3N (#con);
		mIKsolver.effectors:resize(#con);
		kneeIndices:resize(#con)
		axisSign:resize(#con)
		for i=1,#con do
			mIKsolver.effectors(i-1):init(mLoader:getBoneByName(con[i][2]), con[i][3])
			kneeIndices:set(i-1, mLoader:getBoneByName(con[i][1]):treeIndex())
			if con[i].reversed then
				axisSign:set(i-1, -1)
			else
				axisSign:set(i-1, 1)
			end
		end
		--mIK= MotionUtil.createFullbodyIkDOF_limbIK(mLoader.dofInfo, mEffectors, lknee, rknee, true);
		--mIK= MotionUtil.createFullbodyIk_MotionDOF_MultiTarget(mLoader.dofInfo, mEffectors);
		--mIK=MotionUtil.createFullbodyIkDOF_limbIK_straight(mLoader.dofInfo,mEffectors,lknee,rknee);
		mIKsolver.solver=COM_IKsolver(mLoader, mIKsolver.effectors, kneeIndices, axisSign)
	end
end

function eventFunction (ev, val) 
	if ev=='selected' then
		print(mEditConstraints.selectedVertex.." selected")
	elseif ev=='drag_finished' then
		print('drag_finished')

		local range=config.range

		local comTraj=mComTraj
		local editCOMframe=config.editCOMframe
		mCOM=mEditConstraints.conPos(0)/config.skinScale
		genCurve(comTraj:x(), editCOMframe-range[1], mCOM.x)
		genCurve(comTraj:y(), editCOMframe-range[1], mCOM.y)
		genCurve(comTraj:z(), editCOMframe-range[1], mCOM.z)

		dbg.draw('Traj', mComTraj:matView()*config.skinScale, 'COMtraj')

		-- solve IK
		mMotionDOFcontainer.mot:range(range[1], range[2]+1):assign(mOriginalMotion:range(range[1], range[2]+1))
		local conDelta=quaterN(2)
		local importance=vectorn(2)
		for i=range[1], range[2] do

			conDelta(0):assign(quater(1,0,0,0))
			conDelta(1):assign(quater(1,0,0,0))

			local mPose=mMotionDOFcontainer.mot:row(i)
			mLoader:setPoseDOF(mPose)
			mIKsolver.footPos(0):assign(mIKsolver.effectors(0).bone:getFrame().translation)
			mIKsolver.footPos(1):assign(mIKsolver.effectors(1).bone:getFrame().translation)
			local cc=config.constraints
			importance:set(0, cc.leftfoot.importance(i))
			importance:set(1, cc.rightfoot.importance(i))
			local desiredCOM=comTraj(i-range[1]):copy()
			local roottf=MotionDOF.rootTransformation(mPose)
			local rotY=roottf.rotation:rotationY()
			mIKsolver.solver:IKsolve(mPose, rotY, roottf, conDelta, mIKsolver.footPos, importance, desiredCOM);
		end
	end
end
function calcCOMtraj()
	local range=config.range
	local comtraj=vector3N(range[2]-range[1]+1)
	for i=range[1], range[2] do
		mLoader:setPoseDOF(mMotionDOFcontainer.mot:row(i))
		local COM=mLoader:calcCOM()
		comtraj(i-range[1]):assign(COM)

	end
	return comtraj
end

function genCurve(yfn, con_frame, con_mid)

	local numCon=5
	local nvar=yfn:size()
	local h=QuadraticFunctionHardCon(nvar, numCon);

	local y0=yfn(0)
	local y1=yfn(1)
	local yn_1=yfn(nvar-2)
	local yn=yfn(nvar-1)

	-- add(3,0,4,1,5,2,-1) : add objective to minimize (3x+4y+5z-1)^2
	for i=1, nvar-2 do
		-- minimize accelerations : ( -1, 2, -1 ) kernel
		-- (-1* y_{i-1} + 2* y_i - 1*y_{i+1})^2
		h:add(-1, i-1, 2, i, -1, i+1, 0 )
	end
	-- objective function
	-- sum_i (-1* y_{i-1} + 2* y_i - 1*y_{i+1})^2
	-- for 0 <i <=nvar

	-- con(3,0,4,1,5,2,-1) : add constraint(3x+4y+5z-1=0)
	-- 1*y_0 -y0 =0
	-- (y_0: variable)
	-- (y0: constant)
	h:con(1, 0, -y0) 
	h:con(1, 1, -y1) 
	h:con(1, math.floor(con_frame), -con_mid)
	h:con(1, nvar-2, -yn_1) 
	h:con(1, nvar-1, -yn) 

	local x=h:solve()
	yfn:assign(x)
end

function frameMove(fElapsedTime)
end

function onCallback(w, userData)
end

function dtor()
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
end
function handleRendererEvent(ev, button, x,y) 
	if mEditConstraints then
		return mEditConstraints:handleRendererEvent(ev, button, x,y)
	end
	return 0
end
