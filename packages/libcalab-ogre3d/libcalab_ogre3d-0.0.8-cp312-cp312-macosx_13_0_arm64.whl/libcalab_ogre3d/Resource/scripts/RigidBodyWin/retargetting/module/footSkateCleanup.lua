local fc={}
require('moduleIK')

-- example config={
--		filter_size=5,
--		markers={
--			-- testConstraintMarking.lua -> results go to ....fbx.con.lua or ...bvh.con.lua
--			default_param ={
--				thr_speed=0.125, -- speed limit
--				thr_height=0.015,  -- height threshhold (the lower limit)
--			},
--			{
--				"leftToe", 
--				bone='LeftToe', 
--				lpos=vector3(0,0,0),
--			}, {
--				"leftHeel", 
--				bone='leftFoot', 
--				lpos=vector3(0,-0.09,0), -- local position
--			},  
--		}
--	}
function fc.markSingle(config, mLoader, mot, index) 
	local mi=config.markers[index]
	if not config.markers.default_param then
		config.markers.default_param ={
			thr_speed=0.125, -- speed limit
			thr_height=0.002,  -- height threshhold (the lower limit)
		}
	end
	local d=config.markers.default_param
	
	local thr_speed=mi.thr_speed or d.thr_speed
	local thr_heightL = mi.thr_height or d.thr_height

	local markerPosL=matrixn(mot:numFrames(), 3) ;

	local markerBoneL=mLoader:getBoneByName(mi.bone)

	if dbg.lunaType(mot)=='Motion' then
		for i=0, mot:numFrames()-1 do
			mLoader:setPose(mot:pose(i))
			local globalmarkerPosL=markerBoneL:getFrame():toGlobalPos(mi.lpos)
			markerPosL:row(i):setVec3(0, globalmarkerPosL)
		end
		if config.markers.default_param.markerMinHeight then
			local mh=config.markers.default_param.markerMinHeight 
			local min=markerPosL:column(1):minimum()
			if min>mh then
				markerPosL:column(1):rsub(min-mh)
			end
		end
	else
		for i=0, mot:numFrames()-1 do
			mLoader:setPoseDOF(mot:row(i))
			local globalmarkerPosL=markerBoneL:getFrame():toGlobalPos(mi.lpos)
			markerPosL:row(i):setVec3(0, globalmarkerPosL)
		end
	end

	local discontinuity = mot.discontinuity
	if not discontinuity then
		discontinuity=mot:getConstraints(Motion.IS_DISCONTINUOUS)
	end

	local frame_rate=mLoader.dofInfo:frameRate()
	--matrixn:derivative( frame_rate, discontinuity)
	markerVelL=markerPosL:derivative( frame_rate, discontinuity)

	math.filter(markerVelL, config.filter_size)

	markerspeedL=vectorn(markerVelL:rows())
	for i=0, markerVelL:rows()-1 do
		markerspeedL:set(i, markerVelL:row(i):toVector3():length())
	end
	local velRows = markerVelL:rows()
	local conL=boolN(velRows)
	conL:setAllValue(false)

	--constraint deciding
	for i=0, markerVelL:rows()-1 do
		if markerspeedL(i) < thr_speed and markerPosL(i,1) < thr_heightL 
			then

			conL:set(i, true)
		end
	end

	return conL, markerPosL, markerspeedL, {thr_heightL, thr_speed}
end

-- input : conInfo={}, mMotion, config (same as above)
-- output : conInfo.con, conInfo.markerPos
function fc.markConstraints(config, conInfo, loader, mMotion, _optionalMotionInfo, options)
	if type(options) =='boolean' then
		options={ drawSignals=options }
	elseif options==nil then
		options={}
	end
	local drawSignals=options.drawSignals
	assert(type(options)=='table')
	assert(dbg.lunaType(mMotion)=='Motion')
	print('mark all selected!!')
	for i_marker,markerInfo in ipairs(config.markers) do
		--local con, markerPos=mark(config,mLafanLoader, mMotion, i_marker, false)
		local con, markerPos, markerspeed, thr
		if _optionalMotionInfo then
			con=boolN(mMotion:numFrames())
			markerPos=matrixn(mMotion:numFrames(), 3)
			markerspeed=vectorn(mMotion:numFrames())
			for imi, mi in ipairs(_optionalMotionInfo) do
				if options.markerMinHeight then
					config.markers.default_param.markerMinHeight=
					options.markerMinHeight 
				end
				local _con, _markerPos, _markerspeed, _thr=fc.markSingle(config,loader or mi.originalLoader, mi.originalLoader.mMotion, i_marker)
				assert(mi.start+_con:size()<=mMotion:numFrames())
				con:range(mi.start, mi.start+_con:size()):assign(_con)

				markerPos:sub(mi.start, mi.start+_con:size(),0,0):assign(_markerPos)

				markerspeed:range(mi.start, mi.start+_con:size()):assign(_markerspeed)
				thr=_thr
			end
		else
			con, markerPos, markerspeed, thr=fc.markSingle(config,loader or mMotion:skeleton(), mMotion, i_marker)
		end

		if drawSignals then
			local thr_height,thr_speed=unpack(thr) 
			Imp.ChangeChartPrecision(70);
			local pSignalL=Imp.DrawChart(markerspeed:row(), Imp.LINE_CHART, 0, math.min(thr_speed*4, 1), thr_speed);
			RE.motionPanel():scrollPanel():addPanel(pSignalL)
			RE.motionPanel():scrollPanel():setLabel("markerspeed")


			local pSignalL=Imp.DrawChart(markerPos:column(1):copy():row(), Imp.LINE_CHART, 0, thr_height*4, thr_height);
			RE.motionPanel():scrollPanel():addPanel(pSignalL)
			RE.motionPanel():scrollPanel():setLabel("markerheight")
			Imp.DefaultPrecision();
		end

		if not conInfo[i_marker] then
			conInfo[i_marker]={}
		end
		conInfo[i_marker].con=con
		conInfo[i_marker].markerPos=markerPos

		local conpanel=conInfo[i_marker].conPanel

		if not conpanel and (drawSignals  or options.drawCon) then
			conpanel=SelectPanel()
			conInfo[i_marker].conPanel=conpanel
		end
		if conpanel then
			conpanel:release(RE.motionPanel())
			conpanel:init(RE.motionPanel(), markerInfo[1], 1,2)
			conpanel:clear(0, con:size())
			conpanel:drawFrameLines(con:findAll(true))
		end
	end
end

-- example markers 
-- markers={ 
-- {bone='mixamorig:LeftToeBase', lpos=vector3(0,0,0), },
-- {bone='mixamorig:RightToeBase', lpos=vector3(0,0,0), },
-- }

function fc.getMarkerTraj(markers, loader, mMotionDOF)
	local nf=mMotionDOF:rows()
	local feetTraj={}
	local bones={}

	if type(markers[1].bone)=='string' then
		for i, marker in ipairs(markers) do
			feetTraj[i]= vector3N(nf)
			bones[i]=loader:getBoneByName(marker.bone)
		end
	else
		for i, marker in ipairs(markers) do
			feetTraj[i]= vector3N(nf)
			bones[i]=marker.bone
		end
	end

	for i=0, mMotionDOF:rows()-1 do
		loader:setPoseDOF(mMotionDOF:row(i))

		for c, marker in ipairs(markers) do
			local conpos
			local lpos=marker.lpos
			local gpos=bones[c]:getFrame()*lpos
			feetTraj[c](i):assign(gpos)
		end
	end
	return feetTraj
end

-- unlike fc.removeFeetSliding, this function requires both toe and heel constraints marked seperately.
-- example con 
--	con={
--	head={  bone='mixamorig:Head', lpos=vector3(0,0,0), },
--		{
--			"leftToe", 
--			con =boolN.init('[1111111111]')
--			marker= { bone='mixamorig:LeftToeBase', lpos=vector3(0,0,0), },
--		}, {
--			"leftHeel", 
--			con =boolN.init('[1111100000]'), marker= { bone='mixamorig:leftFoot', lpos=vector3(0,-0.09,0), },
--		},
--		... any number of limbs is okay.
--	}
-- option={debugDraw=false, startFrame=0, endFrame=1e5}
function fc.removeFeetSlidingHeelAndToe(con, mLoader, mMotionDOF, option)
	local res=fc.removeFeetSlidingHeelAndToe_part1(con, mLoader, mMotionDOF, option)
	fc.removeFeetSlidingHeelAndToe_part2(res, con, mLoader, mMotionDOF, option)
end
function fc.removeFeetSlidingHeelAndToe_part1(con, mLoader, mMotionDOF, option)
	if not option then
		option={
			useLimbIK=false, 
		}
	end

	if not option.startFrame then
		option.startFrame=0
	end
	if not option.endFrame or option.endFrame>mMotionDOF:numFrames() then
		option.endFrame=mMotionDOF:numFrames()
	end

	local loader=mLoader 
	assert(loader)
	local markers={}
	if #con==0 then
		assert(con.leftToe) assert(con.leftHeel) assert(con.rightToe) assert(con.rightHeel)
		con[1]=con.leftToe
		con[2]=con.leftHeel
		con[3]=con.rightToe
		con[4]=con.rightHeel
		con[1][1]='leftToe'
		con[2][1]='leftHeel'
		con[3][1]='rightToe'
		con[4][1]='rightHeel'
		con.leftToe=nil con.leftHeel=nil con.rightToe=nil con.rightHeel=nil
	end
	for i,v in ipairs(con) do
		if v.marker then
			markers[i]=v.marker
		else
			assert(v.bone and v.lpos)
			markers[i]={
				bone=v.bone,
				lpos=v.lpos,
			}
		end
	end

	-- 원본 모캡의 발 미끄럼 잡기
	local s=option.startFrame
	local e=option.endFrame

	local feetTraj=fc.getMarkerTraj(markers, loader, mMotionDOF:range(option.startFrame, option.endFrame))
	local adjustHeight=option.adjustHeight or function(pos) return 0.0 end -- for adjusting support positions
	local ilimb=#con/2

	if adjustHeight then
		for limb=1, ilimb do
			local con_limb=con[limb*2-1].con:range(s,e):bitwiseOR( con[limb*2].con:range(s,e))
			fc.removePenetration(con_limb, feetTraj[limb*2-1], feetTraj[limb*2], adjustHeight)
		end
	end
	if not option.skipSlidingRemoval then
		for limb=1, ilimb do

			if markers[limb*2-1].bone==markers[limb*2].bone then
				local footLen=markers[limb*2-1].lpos:distance(markers[limb*2].lpos)
				fc.removeSlidingHeelAndToe_v2(footLen, con[limb*2-1].con, con[limb*2].con, feetTraj[limb*2-1], feetTraj[limb*2], adjustHeight)
			else
				local con_limb=con[limb*2-1].con:range(s,e):bitwiseOR( con[limb*2].con:range(s,e))
				fc.removeSlidingHeelAndToe(con_limb, feetTraj[limb*2-1], feetTraj[limb*2], adjustHeight)
			end
		end
	end
	return {markers, feetTraj}
end
function fc.removeFeetSlidingHeelAndToe_part2(part1_result, con, mLoader, mMotionDOF, option)

	local loader=mLoader
	local markers, feetTraj=unpack(part1_result)
	local s=option.startFrame
	local e=option.endFrame

	local limbs={}
	for i, marker in ipairs(markers) do
		limbs[i]={ marker.bone, marker.lpos}
	end

	local originalMot=mMotionDOF:copy()
	local mSolverInfo
	do
		-- numerical ik (results go to originalMot)
		mSolverInfo=fc.createIKsolver(loader, limbs)

		assert(con.head)
		local headBone=loader:getBoneByName(con.head.bone)
		print(s,e)
		for iframe=s, e-1 do
			if math.fmod(iframe, 100)==0 then
				io.write('.')
				io.flush()
			end
			local pose=mMotionDOF:row(iframe):copy()

			local numCon=mSolverInfo.numCon
			local footPos=vector3N (numCon);

			for j=0, numCon-1 do
				footPos(j):assign(feetTraj[j+1](iframe-s)) 
			end

			local mIK=mSolverInfo.solver
			local mEffectors=mSolverInfo.effectors
			--local prev_roottf=MotionDOF.rootTransformation(pose)
			--local toLocal=prev_roottf:inverse()
			local toLocal=MotionDOF.rootTransformation(pose):inverse()
			toLocal.translation.y=0
			toLocal.rotation:assign(toLocal.rotation:rotationY())

			local useHead=1
			mIK:_changeNumEffectors(numCon)
			mIK:_changeNumConstraints(useHead)
			if useHead==1 then
				local loader=mSolverInfo.loader
				--local headRefPose=loader.dofInfo:blendPose( nextPose1, nextPose2, 0.1)
				loader:setPoseDOF(pose)
				headPos=headBone:getFrame()*con.head.lpos
			end

			mIK:setParam('damping_weight', 0.01,0.01)

			for i=0,numCon-1 do
				mIK:_setEffector(i, mEffectors(i).bone, mEffectors(i).localpos)
				footPos(i):assign(toLocal*footPos(i))
			end
			if useHead==1 then
				local i=numCon
				local wHead_y=0.0001
				mIK:_setPositionConstraint(0, headBone, con.head.lpos, toLocal*headPos, 1,wHead_y ,0.1 );
			end

			mIK:_effectorUpdated()
			MotionDOF.setRootTransformation(pose, toLocal*MotionDOF.rootTransformation(pose))
			mIK:IKsolve(pose, footPos)


			MotionDOF.setRootTransformation(pose, toLocal:inverse()*MotionDOF.rootTransformation(pose))
			mMotionDOF:row(iframe):assign(pose)
		end
		print('_')
	end
	if option.useLimbIK then
		if true then
			-- use the spine joints (including the root) of the numerical IK results. 
			local delta=originalMot:diff(mMotionDOF)
			math.filter(delta, 30)
			originalMot:patch(delta)
			local bone=loader:getBoneByName(con.head.bone)
			while bone:treeIndex()>=1 do
				local si=loader.dofInfo:startT(bone:treeIndex())
				local ei=loader.dofInfo:endR(bone:treeIndex())
				if ei>si then
					mMotionDOF:sub(0,0,si, ei):assign(originalMot:sub(0,0,si,ei))
				end
				bone=bone:parent()
			end
		else
			-- use only the root translation of the numerical IK results.
			mMotionDOF:sub(0,0,0,3):assign(originalMot:sub(0,0,0,3))
		end


		-- use only root of the fullIK results.
		assert(#con==4)
		assert(con[1].bone==con[2].bone)
		assert(con[3].bone==con[4].bone)
		assert(con[1][1]=='leftToe')
		assert(con[2][1]=='leftHeel')
		assert(con[3][1]=='rightToe')
		assert(con[4][1]=='rightHeel')


		ankle1=loader:getBoneByName(con[1].bone)
		ankle2=loader:getBoneByName(con[3].bone)
		local IKconfig={
		}
		
		IKconfig[1]={
			ankle1:parent():name(), ankle1:name(), con[2].lpos, reversed=false, childCon=2
		}
		IKconfig[2]={
			-- toe
			ankle1:parent():name(), ankle1:name(), con[1].lpos, 
		}
		
		IKconfig[3]={
			ankle2:parent():name(), ankle2:name(), con[4].lpos, reversed=false, childCon=4
		}
		IKconfig[4]={
			-- toe
			ankle2:parent():name(), ankle2:name(), con[3].lpos, 
		}

		local mSolverInfo=createIKsolver(solvers.LimbIKsolverT, loader, IKconfig)

		mSolverInfo.solver:setOption('lengthAdjust', true)
		MotionUtil.setMaxLengthAdjustmentRatio(0.1)
		--local rootTraj=originalMot:copy()
		--rootTraj:patch(delta)
		--originalMot:sub(0,0,0,7):assign(rootTraj:sub(0,0,0,7))

		local pass2_initial=originalMot:copy()

		local importance=CT.vec(1,1)

		local conpos=vector3N(4)
		local ik=mSolverInfo.solver
		local lenAdjustAll=CT.ones(mMotionDOF:rows(), loader:numBone())
		assert(e<=mMotionDOF:rows())
		print('limbik', s,e)
		for i=s, e-1 do
			if math.fmod(i, 200)==0 then
				io.write('.')
				io.flush()
			end
			conpos(0):assign(feetTraj[2](i-s)) 
			conpos(1):assign(feetTraj[1](i-s)) 
			conpos(2):assign(feetTraj[4](i-s)) 
			conpos(3):assign(feetTraj[3](i-s)) 
			local lenAdjust=ik:IKsolve(originalMot:row(i), conpos)
			lenAdjustAll:row(i):assign(lenAdjust)
		end
		local delta=pass2_initial:diff(originalMot)
		math.filter(delta, 5)
		pass2_initial:patch(delta)


		mMotionDOF:assign(pass2_initial)
		math.filter(lenAdjustAll,5)

		return lenAdjustAll, feetTraj
	else
		local delta=originalMot:diff(mMotionDOF)
		math.filter(delta, 5)
		originalMot:patch(delta)
		mMotionDOF:assign(originalMot)
	end


	if option.debugDraw then
		for c=1,4 do
			dbg.namedDraw('Traj', feetTraj[c]:matView()*100, 'feet'..c)
		end
	end
	return mSolverInfo, feetTraj
end
-- boolN con, 
-- matrixn traj (global positions : n by 3), 
-- [function adjustHeight(pos) returns y] -- for support positions
-- [function clearGroundTraj(traj, s, e)] -- for swing traj
function fc.removeSliding(con, traj, adjustHeight, clearGroundTraj)
	local ii=intIntervals()
	ii:runLengthEncode(con)
	for icontact=0, ii:size()-1  do
		local si=ii:startI(icontact)
		local ei=ii:endI(icontact)
		local prev_ei=nil
		local next_si=nil
		if icontact > 0 then
			prev_ei=ii:endI(icontact-1)
		end
		if icontact <ii:size()-1 then
			next_si=ii:startI(icontact+1)
		end
		local avgPos=vector3(0,0,0)
		for i=si, ei-1 do
			local data=traj:row(i)
			avgPos:radd(data:toVector3(0))
		end
		avgPos:scale(1.0/(ei-si))
		if adjustHeight then
			avgPos.y=adjustHeight(avgPos)
		end

		local err1=avgPos-traj:row(si):toVector3(0)
		local err2=avgPos-traj:row(ei-1):toVector3(0)

		local minWindow=15
		if prev_ei then
			for i=prev_ei, si-1 do
				local data=traj:row(i)
				local s=sop.smoothMapA(i, prev_ei-1, si, 0,1)
				data:setVec3(0, data:toVector3(0)+err1*s)
			end
			if clearGroundTraj then clearGroundTraj(traj, prev_ei, si) end
		elseif si>0 then
			for i=0, si-1 do
				local data=traj:row(i)
				local s=sop.smoothMapA(i, math.min(0, si-minWindow), si, 0,1)
				data:setVec3(0, data:toVector3(0)+err1*s)
			end
			if clearGroundTraj then clearGroundTraj(traj, 0, si) end
		end

		if nsi then
			for i=ei, nsi-1 do
				local data=traj:row(i)
				local s=sop.smoothMapB(i, ei-1, nsi, 1,0)
				data:setVec3(0, data:toVector3(0)+err2*s)
			end
			if clearGroundTraj then clearGroundTraj(traj, ei, nsi) end
		elseif ei<traj:rows() then
			local nf=traj:rows()
			for i=ei, nf-1 do
				local data=traj:row(i)
				local s=sop.smoothMapB(i, ei-1, math.max(nf, ei+minWindow), 1,0)
				data:setVec3(0, data:toVector3(0)+err2*s)
			end
			if clearGroundTraj then clearGroundTraj(traj, ei, nsi) end

		end
		local nf=traj:rows()
		for i=si, ei-1 do
			local data=traj:row(i)
			data:setVec3(0, avgPos)
		end
	end
end
function fc.adjustContactLocations(con, traj, newPos)
	local ii=intIntervals()
	ii:runLengthEncode(con)
	assert(ii:size()==newPos:size())
	for icontact=0, ii:size()-1  do
		local si=ii:startI(icontact)
		local ei=ii:endI(icontact)
		local prev_ei=nil
		local next_si=nil
		if icontact > 0 then
			prev_ei=ii:endI(icontact-1)
		end
		if icontact <ii:size()-1 then
			next_si=ii:startI(icontact+1)
		end
		local avgPos=newPos(icontact)

		local err1=avgPos-traj:row(si):toVector3(0)
		local err2=avgPos-traj:row(ei-1):toVector3(0)

		if prev_ei then
			for i=prev_ei, si-1 do
				local data=traj:row(i)
				local s=sop.map(i, prev_ei-1, si, 0,1)
				data:setVec3(0, data:toVector3(0)+err1*s)
			end
		elseif si>0 then
			for i=0, si-1 do
				local data=traj:row(i)
				local s=sop.map(i, 0, si, 0,1)
				data:setVec3(0, data:toVector3(0)+err1*s)
			end
		end

		if nsi then
			for i=ei, nsi-1 do
				local data=traj:row(i)
				local s=sop.map(i, ei-1, nsi, 1,0)
				data:setVec3(0, data:toVector3(0)+err2*s)
			end
		elseif ei<traj:rows() then
			local nf=traj:rows()
			for i=ei, nf-1 do
				local data=traj:row(i)
				local s=sop.map(i, ei-1, nf, 1,0)
				data:setVec3(0, data:toVector3(0)+err2*s)
			end

		end
		local nf=traj:rows()
		for i=si, ei-1 do
			local data=traj:row(i)
			data:setVec3(0, avgPos)
		end
	end
end

-- feet_config= { toe=vector3(0, -0.05, 0.14), -- local pos of toe,
--                  heel=vector3(0, -0.10, 0.06),} -- local pos of heel
-- returns { rtoe, rheel, ltoe, lheel}
function fc.getFeetTraj(feet_config, loader, mMotionDOF)
	local nf=mMotionDOF:numFrames()
	local feetTraj={
		vector3N(nf),  -- R toe
		vector3N(nf), 
		vector3N(nf),  -- L toe
		vector3N(nf), 
	}

	for i=0, mMotionDOF:numFrames()-1 do
		loader:setPoseDOF(mMotionDOF:row(i))

		for c=1, 4 do

			local conpos
			local lpos=feet_config.heel
			if math.fmod(c-1,2)==0 then
				lpos=feet_config.toe
			end
			local gpos
			if c<=2 then
				gpos=loader:getBoneByVoca(MotionLoader.RIGHTANKLE):getFrame()*lpos
			else
				gpos=loader:getBoneByVoca(MotionLoader.LEFTANKLE):getFrame()*lpos
			end
			feetTraj[c](i):assign(gpos)
		end
	end

	return feetTraj
end

-- con={conRfoot, conLfoot}
-- feet_config= { toe=vector3(0, -0.05, 0.14), -- local pos of toe,
--                  heel=vector3(0, -0.10, 0.06),} -- local pos of heel
-- option={debugDraw=false}
-- mLoader should already have "setVoca"-called.
function fc.removeFeetSliding(con, feet_config, mLoader, mMotionDOF, option)
	if not option then
		option={}
	end

	local loader=mLoader
	-- 원본 모캡의 발 미끄럼 잡기

	local feetTraj=fc.getFeetTraj(feet_config, loader, mMotionDOF)
	local adjustHeight=function(x) return 0.0 end
	fc.removeSlidingHeelAndToe(con[1], feetTraj[1], feetTraj[2], adjustHeight)
	fc.removeSlidingHeelAndToe(con[2], feetTraj[3], feetTraj[4], adjustHeight)

	mSolverInfo=fc.createIKsolver(loader, input.limbs)

	for i=0, mMotionDOF:rows()-1 do
		local pose=mMotionDOF:row(i):copy()

		local numCon=mSolverInfo.numCon
		local footPos=vector3N (numCon);

		footPos(0):assign(feetTraj[3](i)) -- L toe (see info_hyunwooLowDOF.lua)
		footPos(1):assign(feetTraj[4](i))
		footPos(2):assign(feetTraj[1](i)) -- R toe
		footPos(3):assign(feetTraj[2](i))

		local mIK=mSolverInfo.solver
		local mEffectors=mSolverInfo.effectors
		--local prev_roottf=MotionDOF.rootTransformation(pose)
		--local toLocal=prev_roottf:inverse()
		local toLocal=MotionDOF.rootTransformation(pose):inverse()
		toLocal.translation.y=0
		toLocal.rotation:assign(toLocal.rotation:rotationY())

		local useHead=1
		mIK:_changeNumEffectors(numCon)
		mIK:_changeNumConstraints(useHead)
		if useHead==1 then
			local loader=mSolverInfo.loader
			--local headRefPose=loader.dofInfo:blendPose( nextPose1, nextPose2, 0.1)
			loader:setPoseDOF(pose)
			headBone=loader:getBoneByName(input.head[1])
			headPos=headBone:getFrame()*input.head[2]
		end

		mIK:setParam('damping_weight', 0.01,0.01)

		for i=0,numCon-1 do
			mIK:_setEffector(i, mEffectors(i).bone, mEffectors(i).localpos)
			footPos(i):assign(toLocal*footPos(i))
		end
		if useHead==1 then
			local i=numCon
			local wHead_y=0.0001
			mIK:_setPositionConstraint(0, headBone, input.head[2], toLocal*headPos, 1,wHead_y ,0.1 );
		end

		mIK:_effectorUpdated()
		MotionDOF.setRootTransformation(pose, toLocal*MotionDOF.rootTransformation(pose))
		mIK:IKsolve(pose, footPos)


		MotionDOF.setRootTransformation(pose, toLocal:inverse()*MotionDOF.rootTransformation(pose))
		mMotionDOF:row(i):assign(pose)
	end
	if option.debugDraw then
		for c=1,4 do
			dbg.namedDraw('Traj', feetTraj[c]:matView()*100, 'feet'..c)
		end
	end
end

function fc.getContactPos(mLoader, ref_pose, limb, feet_config)
	mLoader:setPoseDOF(ref_pose)

	local ankle_tf
	if limb==1 then
		ankle_tf=mLoader:getBoneByVoca(MotionLoader.RIGHTANKLE):getFrame()
	else
		ankle_tf=mLoader:getBoneByVoca(MotionLoader.LEFTANKLE):getFrame()
	end

	local toe=ankle_tf*feet_config.toe
	local heel=ankle_tf*feet_config.heel
	local footlen=heel:distance(toe)

	if toe.y < heel.y then
		-- toe contact
		local heelDir=heel-toe
		heelDir.y=0
		heelDir:normalize()
		heel=toe+heelDir*footlen
	else
		-- heel contact
		local toeDir=toe-heel
		toeDir.y=0
		toeDir:normalize()
		toe=heel+toeDir*footlen
	end
	return  toe*0.5+heel*0.5
end
local function midPos(toetraj, heeltraj, i, footlen)
	local toe=toetraj:row(i):toVector3(0)
	local heel=heeltraj:row(i):toVector3(0)
	if not footlen then
		footlen=heel:distance(toe)
	end

	if toe.y < heel.y then
		-- toe contact
		local heelDir=heel-toe
		heelDir.y=0
		heelDir:normalize()
		heel=toe+heelDir*footlen
	else
		-- heel contact
		local toeDir=toe-heel
		toeDir.y=0
		toeDir:normalize()
		toe=heel+toeDir*footlen
	end
	return toe*0.5+heel*0.5
end
function fc.getMidPosTraj(toetraj, heeltraj, footlen)
	if dbg.lunaType(toetraj):sub(1,8)=='vector3N' then
		toetraj=toetraj:matView()
	end
	if dbg.lunaType(heeltraj):sub(1,8)=='vector3N' then
		heeltraj=heeltraj:matView()
	end
	local midTraj=toetraj:copy()
	for i=0, toetraj:rows()-1 do
		midTraj:row(i):setVec3(0, midPos(toetraj, heeltraj, i, footlen))
	end
	return midTraj
end

-- returns conPos(vector3N), con_intervals(intIntervals), conToe(boolN), conHeel(boolN)
function fc.getContactPositions(con, toetraj, heeltraj)
	if dbg.lunaType(toetraj):sub(1,8)=='vector3N' then
		toetraj=toetraj:matView()
	end
	if dbg.lunaType(heeltraj):sub(1,8)=='vector3N' then
		heeltraj=heeltraj:matView()
	end
	local ii=intIntervals()
	ii:runLengthEncode(con)

	local conToe=boolN(con:size())
	local conHeel=boolN(con:size())
	local conPos=vector3N(ii:size())

	for icontact=0, ii:size()-1  do
		local si=ii:startI(icontact)
		local ei=ii:endI(icontact)
		local avgPos=vector3(0,0,0)


		for i=si, ei-1 do
			avgPos:radd(midPos(toetraj, heeltraj, i))

			local toe=toetraj:row(i):toVector3(0)
			local heel=heeltraj:row(i):toVector3(0)
			local thr=0.01
			if toe.y < heel.y-thr then
				conToe:set(i, true)
			elseif heel.y < toe.y-thr then
				conHeel:set(i, true)
			else
				conToe:set(i, true)
				conHeel:set(i, true)
			end
		end
		avgPos:scale(1.0/(ei-si))
		conPos(icontact):assign(avgPos)
	end
	return conPos, ii, conToe, conHeel
end
function fc.getTransformedTraj(bonetraj, localpos)
	if dbg.lunaType(bonetraj):sub(1,8)=='vector3N' then
		bonetraj=bonetraj:matView()
	end
	if dbg.lunaType(localpos):sub(1,8)=='vector3N' then
		localpos=localpos:matView()
	end
	local out=vector3N(bonetraj:rows())
	if dbg.lunaType(localpos)=='vector3' then
		for iframe=0, bonetraj:rows()-1 do
			out(iframe):assign(bonetraj:row(i):toTransf()*localpos)
		end
	else
		for iframe=0, bonetraj:rows()-1 do
			out(iframe):assign(bonetraj:row(i):toTransf()*localpos:row(i):toVector3())
		end
	end
	return out
end
function fc.getConstraintPositions(con, inputpos)
	local ii=intIntervals()
	ii:runLengthEncode(con)

	local conPos=vector3N(ii:size())
	for icontact=0, ii:size()-1  do
		local si=ii:startI(icontact)
		local ei=ii:endI(icontact)
		local avgPos=vector3(0,0,0)
		for i=si, ei-1 do
			avgPos:radd(inputpos:row(i):toVector3())
		end
		avgPos:scale(1.0/(ei-si))
		conPos(icontact):assign(avgPos)
	end
	return conPos, ii
end

-- input: con={conR, conL}, feetTraj={ rtoe, rheel, ltoe, heel }
-- output: { { vector3N(), boolN(), boolN()}, -- R conPos, conToe, conHeel
--			{ vector3N(), boolN(), boolN()}, -- L conPos, conToe, conHeel
--		}
function fc.getContactPositionsMultiClip(discontinuity, con, feetTraj)
	--  consider discontinuity in the reference motion.
	local segFinder=SegmentFinder(discontinuity)

	local conPos={
		{ vector3N(), boolN(), boolN()}, -- R conPos, conToe, conHeel
		{ vector3N(), boolN(), boolN()}, -- L conPos, conToe, conHeel
	}

	local nf=discontinuity:size()
	for ilimb=1, 2 do
		conPos[ilimb][1]:setSize(nf)
		conPos[ilimb][2]:setSize(nf)
		conPos[ilimb][3]:setSize(nf)

		for i=0, segFinder:numSegment()-1 do
			local s=segFinder:startFrame(i)
			local e=segFinder:endFrame(i)


			local conpos, ii, conToe, conHeel=fc.getContactPositions(con[ilimb]:range(s,e), feetTraj[ilimb*2-1]:range(s,e), feetTraj[ilimb*2]:range(s,e))

			for j=0, ii:numInterval()-1 do
				conPos[ilimb][1]:range(s+ii:startI(j),s+ii:endI(j)):setAllValue(conpos(j))
			end
			conPos[ilimb][2]:range(s,e):assign(conToe)
			conPos[ilimb][3]:range(s,e):assign(conHeel)
		end
	end
	return conPos
end
-- input parameters:
-- boolN con, 
-- matrixn toetraj (global positions : n by 3), 
-- matrixn heeltraj (global positions : n by 3), 
-- [function adjustHeight(pos) returns y] -- for support positions
-- [function clearGroundTraj(toetraj, heeltraj, s, e)] -- for swing traj
--
function fc.removeSlidingHeelAndToe(con, toetraj, heeltraj, adjustHeight, clearGroundTraj)

	if dbg.lunaType(toetraj):sub(1,8)=='vector3N' then
		toetraj=toetraj:matView()
	end
	if dbg.lunaType(heeltraj):sub(1,8)=='vector3N' then
		heeltraj=heeltraj:matView()
	end


	if false then
		-- only for debugging
		for i=0, toetraj:rows()-1 do
			toetraj:row(i):setVec3(0, midPos(toetraj, heeltraj, i))
		end
		return 
	end

	local conPos, ii, conToe, conHeel=fc.getContactPositions(con, toetraj, heeltraj)

	for icontact=0, ii:size() -1 do
		local si=ii:startI(icontact)
		local ei=ii:endI(icontact)
		local prev_ei=nil
		local next_si=nil
		if icontact > 0 then
			prev_ei=ii:endI(icontact-1)
		end
		if icontact <ii:size()-1 then
			next_si=ii:startI(icontact+1)
		end
		local avgPos=conPos(icontact)

		if adjustHeight then
			avgPos.y=adjustHeight(avgPos)
		end

		--dbg.draw('Sphere', avgPos*100, RE.generateUniqueName())

		local err1=avgPos-midPos(toetraj, heeltraj, si)
		local err2=avgPos-midPos(toetraj, heeltraj, ei-1)

		local minWindow=15
		if prev_ei then
			for i=prev_ei, si-1 do
				local s=sop.smoothMapA(i, prev_ei-1, si, 0,1)
				local data
				data=toetraj:row(i)
				data:setVec3(0, data:toVector3(0)+err1*s)
				data=heeltraj:row(i)
				data:setVec3(0, data:toVector3(0)+err1*s)
			end
			if clearGroundTraj then clearGroundTraj(toetraj, heeltraj, prev_ei, si) end
		elseif si>0 then
			for i=0, si-1 do
				local s=sop.smoothMapA(i, math.min(0, si-minWindow), si, 0,1)
				local data
				data=toetraj:row(i)
				data:setVec3(0, data:toVector3(0)+err1*s)
				data=heeltraj:row(i)
				data:setVec3(0, data:toVector3(0)+err1*s)
			end
			if clearGroundTraj then clearGroundTraj(toetraj, heeltraj, 0, si) end
		end

		if nsi then
			for i=ei, nsi-1 do
				local s=sop.smoothMapB(i, ei-1, nsi, 1,0)
				local data
				data=toetraj:row(i)
				data:setVec3(0, data:toVector3(0)+err2*s)
				data=heeltraj:row(i)
				data:setVec3(0, data:toVector3(0)+err2*s)
			end
			if clearGroundTraj then clearGroundTraj(toetraj,heeltraj, ei, nsi) end
		elseif ei<toetraj:rows() then
			local nf=toetraj:rows()
			for i=ei, nf-1 do
				local s=sop.smoothMapB(i, ei-1, math.max(nf, ei+minWindow), 1,0)
				local data
				data=toetraj:row(i)
				data:setVec3(0, data:toVector3(0)+err2*s)
				data=heeltraj:row(i)
				data:setVec3(0, data:toVector3(0)+err2*s)
			end
			if clearGroundTraj then clearGroundTraj(toetraj, heeltraj, ei, nsi) end

		end

		local nf=toetraj:rows()
		for i=si, ei-1 do
			local err=avgPos-midPos(toetraj, heeltraj, i)

			local data
			data=toetraj:row(i)
			data:setVec3(0, data:toVector3(0)+err)
			data=heeltraj:row(i)
			data:setVec3(0, data:toVector3(0)+err)
		end
	end

	fc.removeSliding(conToe, toetraj, adjustHeight)
	fc.removeSliding(conHeel, heeltraj, adjustHeight)


end

function fc.getContactPositions_v2(footLen, conToe, conHeel, toetraj, heeltraj)
	if dbg.lunaType(toetraj):sub(1,8)=='vector3N' then
		toetraj=toetraj:matView()
	end
	if dbg.lunaType(heeltraj):sub(1,8)=='vector3N' then
		heeltraj=heeltraj:matView()
	end
	local conPos, conDir, ii
	-- getcontactpositions (v2)
	local con=conToe:bitwiseOR(conHeel)
	local con_both=conToe:bitwiseAND(conHeel)
	ii=intIntervals()
	ii:runLengthEncode(con)
	conPos=vector3N(ii:size())
	conDir=vector3N(ii:size())
	for icontact=0, ii:size()-1  do
		local si=ii:startI(icontact)
		local ei=ii:endI(icontact)
		if con_both:range(si,ei):count()==0 then
			con_both:set(math.floor((si+ei)/2), true)
		end
		local avgPos=vector3(0,0,0)
		local avgToeDir=vector3(0,0,0)
		for i=si, ei -1 do
			if con_both(i) then
				avgPos:radd(midPos(toetraj, heeltraj, i, footLen))
				avgToeDir:radd(toetraj:row(i):toVector3()-heeltraj:row(i):toVector3())
			end
		end
		avgPos:rdiv(con_both:range(si,ei):count())
		avgToeDir.y=0
		avgToeDir:normalize()

		conPos(icontact):assign(avgPos)
		conDir(icontact):assign(avgToeDir)
	end
	return conPos, conDir, ii
end
function fc.getContactPositions_stair(conToe, conHeel, centertraj)
	if dbg.lunaType(centertraj):sub(1,8)=='vector3N' then
		centertraj=centertraj:matView()
	end
	local conPos, ii
	-- getcontactpositions (v2)
	local con=conToe:bitwiseOR(conHeel)
	local con_both=conToe:bitwiseAND(conHeel)
	ii=intIntervals()
	ii:runLengthEncode(con)
	conPos=vector3N(ii:size())
	for icontact=0, ii:size()-1  do
		local si=ii:startI(icontact)
		local ei=ii:endI(icontact)
		if con_both:range(si,ei):count()==0 then
			con_both:set(math.floor((si+ei)/2), true)
		end
		local avgPos=vector3(0,0,0)
		for i=si, ei -1 do
			if con_both(i) then
				avgPos:radd(centertraj:row(i):toVector3(0))
			end
		end
		avgPos:rdiv(con_both:range(si,ei):count())

		conPos(icontact):assign(avgPos)
	end
	return conPos, ii
end
function fc.removeSlidingHeelAndToe_v2(footLen, conToe, conHeel, toetraj, heeltraj, adjustHeight, clearGroundTraj)

	if dbg.lunaType(toetraj):sub(1,8)=='vector3N' then
		toetraj=toetraj:matView()
	end
	if dbg.lunaType(heeltraj):sub(1,8)=='vector3N' then
		heeltraj=heeltraj:matView()
	end


	local conPos, conDir, ii=fc.getContactPositions_v2(footLen, conToe, conHeel, toetraj, heeltraj)

	function calcErr(i, conToe, conHeel, toetraj, heeltraj, avgPos, avgDir, footLen)
		if conToe(i) then
			local err=avgPos+avgDir*(footLen*0.5) -toetraj:row(i):toVector3()
			return err
		else
			local err=avgPos-avgDir*(footLen*0.5) -heeltraj:row(i):toVector3()
			return err
		end
	end

	for icontact=0, ii:size() -1 do
		local si=ii:startI(icontact)
		local ei=ii:endI(icontact)
		local prev_ei=nil
		local next_si=nil
		if icontact > 0 then
			prev_ei=ii:endI(icontact-1)
		end
		if icontact <ii:size()-1 then
			next_si=ii:startI(icontact+1)
		end
		local avgPos=conPos(icontact)

		if adjustHeight then
			avgPos.y=adjustHeight(avgPos)
		end

		--dbg.draw('Sphere', avgPos*100, RE.generateUniqueName())

		local err1=calcErr(si, conToe, conHeel, toetraj, heeltraj, avgPos, conDir(icontact), footLen)
		local err2=calcErr(ei-1, conToe, conHeel, toetraj, heeltraj, avgPos, conDir(icontact), footLen)

		local minWindow=15
		if prev_ei then
			for i=prev_ei, si-1 do
				local s=sop.smoothMapA(i, prev_ei-1, si, 0,1)
				local data
				data=toetraj:row(i)
				data:setVec3(0, data:toVector3(0)+err1*s)
				data=heeltraj:row(i)
				data:setVec3(0, data:toVector3(0)+err1*s)
			end
			if clearGroundTraj then clearGroundTraj(toetraj, heeltraj, prev_ei, si) end
		elseif si>0 then
			for i=0, si-1 do
				local s=sop.smoothMapA(i, math.min(0, si-minWindow), si, 0,1)
				local data
				data=toetraj:row(i)
				data:setVec3(0, data:toVector3(0)+err1*s)
				data=heeltraj:row(i)
				data:setVec3(0, data:toVector3(0)+err1*s)
			end
			if clearGroundTraj then clearGroundTraj(toetraj, heeltraj, 0, si) end
		end

		if nsi then
			for i=ei, nsi-1 do
				local s=sop.smoothMapB(i, ei-1, nsi, 1,0)
				local data
				data=toetraj:row(i)
				data:setVec3(0, data:toVector3(0)+err2*s)
				data=heeltraj:row(i)
				data:setVec3(0, data:toVector3(0)+err2*s)
			end
			if clearGroundTraj then clearGroundTraj(toetraj,heeltraj, ei, nsi) end
		elseif ei<toetraj:rows() then
			local nf=toetraj:rows()
			for i=ei, nf-1 do
				local s=sop.smoothMapB(i, ei-1, math.max(nf, ei+minWindow), 1,0)
				local data
				data=toetraj:row(i)
				data:setVec3(0, data:toVector3(0)+err2*s)
				data=heeltraj:row(i)
				data:setVec3(0, data:toVector3(0)+err2*s)
			end
			if clearGroundTraj then clearGroundTraj(toetraj, heeltraj, ei, nsi) end

		end

		local nf=toetraj:rows()
		for i=si, ei-1 do
			local err=calcErr(i, conToe, conHeel, toetraj, heeltraj, avgPos, conDir(icontact), footLen)

			local data
			data=toetraj:row(i)
			data:setVec3(0, data:toVector3(0)+err)
			data=heeltraj:row(i)
			data:setVec3(0, data:toVector3(0)+err)
		end
	end

	fc.removeSliding(conToe, toetraj, adjustHeight)
	fc.removeSliding(conHeel, heeltraj, adjustHeight)


end

function fc.removePenetration(con, toetraj, heeltraj, adjustHeight)

	if dbg.lunaType(toetraj):sub(1,8)=='vector3N' then
		toetraj=toetraj:matView()
	end
	if dbg.lunaType(heeltraj):sub(1,8)=='vector3N' then
		heeltraj=heeltraj:matView()
	end


	if false then
		-- only for debugging
		for i=0, toetraj:rows()-1 do
			toetraj:row(i):setVec3(0, midPos(toetraj, heeltraj, i))
		end
		return 
	end

	local conPos, ii, conToe, conHeel=fc.getContactPositions(con, toetraj, heeltraj)

	for icontact=0, ii:size() -1 do
		local si=ii:startI(icontact)
		local ei=ii:endI(icontact)
		local prev_ei=nil
		local next_si=nil
		if icontact > 0 then
			prev_ei=ii:endI(icontact-1)
		end
		if icontact <ii:size()-1 then
			next_si=ii:startI(icontact+1)
		end
		local avgPos=conPos(icontact)

		if adjustHeight then
			avgPos.y=adjustHeight(avgPos)
		end

		--dbg.draw('Sphere', avgPos*100, RE.generateUniqueName())

		local err1=avgPos-midPos(toetraj, heeltraj, si)
		local err2=avgPos-midPos(toetraj, heeltraj, ei-1)
		-- adjust height only using picewise-linear curves
		err1.x=0
		err1.z=0
		err2.x=0
		err2.z=0

		local minWindow=15
		if prev_ei then
			for i=prev_ei, si-1 do
				local s=sop.map(i, prev_ei-1, si, 0,1)
				local data
				data=toetraj:row(i)
				data:setVec3(0, data:toVector3(0)+err1*s)
				data=heeltraj:row(i)
				data:setVec3(0, data:toVector3(0)+err1*s)
			end
		elseif si>0 then
			for i=0, si-1 do
				local s=sop.map(i, math.min(0, si-minWindow), si, 0,1)
				local data
				data=toetraj:row(i)
				data:setVec3(0, data:toVector3(0)+err1*s)
				data=heeltraj:row(i)
				data:setVec3(0, data:toVector3(0)+err1*s)
			end
		end

		if nsi then
			for i=ei, nsi-1 do
				local s=sop.map(i, ei-1, nsi, 1,0)
				local data
				data=toetraj:row(i)
				data:setVec3(0, data:toVector3(0)+err2*s)
				data=heeltraj:row(i)
				data:setVec3(0, data:toVector3(0)+err2*s)
			end
		elseif ei<toetraj:rows() then
			local nf=toetraj:rows()
			for i=ei, nf-1 do
				local s=sop.map(i, ei-1, math.max(nf, ei+minWindow), 1,0)
				local data
				data=toetraj:row(i)
				data:setVec3(0, data:toVector3(0)+err2*s)
				data=heeltraj:row(i)
				data:setVec3(0, data:toVector3(0)+err2*s)
			end
		end

		local nf=toetraj:rows()
		for i=si, ei-1 do
			local err=avgPos-midPos(toetraj, heeltraj, i)

			local data
			data=toetraj:row(i)
			data:set(1, data(1)+err.y)
			data=heeltraj:row(i)
			data:set(1, data(1)+err.y)
		end
	end
end

function fc.buildContactConstraints(nf, touchDown, touchOff)
	local con={}
	local function contains(td, iframe)
		assert(type(td)=='table')
		for i, td_frame in ipairs(td) do
			if td_frame==iframe then
				return true
			end
		end
		return false
	end
	local numCon=#touchDown
	for i_con=1, numCon do
		con[i_con]=boolN()
		local c=con[i_con]
		c:resize(nf)
		c:setAllValue(false)
		local ccon=false
		local td=touchDown[i_con]
		local toff=touchOff[i_con]
		for iframe=0, nf-1 do
			if contains(td, iframe) then
				-- start touchDown
				ccon=true
			elseif contains(toff, iframe) then
				-- start swing
				ccon=false
			end
			c:set(iframe, ccon)
		end
	end
	return con
end
function fc.createIKsolver(loader, config)
	local out={}
	local mEffectors=MotionUtil.Effectors()
	local numCon=#config
	mEffectors:resize(numCon);
	out.loader=loader
	out.effectors=mEffectors
	out.numCon=numCon
	local kneeDofs=vectorn()

	for i=0, numCon-1 do
		local conInfo=config[i+1]
		local kneeInfo=1
		if #conInfo==2 then
			kneeInfo=0
		end
		mEffectors(i):init(loader:getBoneByName(conInfo[kneeInfo+1]), conInfo[kneeInfo+2])
		if kneeInfo~=0 then
			kneeDofs:pushBack(loader.dofInfo:startR(loader:getBoneByName(conInfo[kneeInfo]):treeIndex()))
		end
	end
	if kneeDofs:size()>0 then
		out.kneeDOFs=kneeDofs
	end
	--out.solver=MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_lbfgs(loader.dofInfo, mEffectors,g_con);
	out.solver=MotionUtil.createFullbodyIk_MotionDOF_MultiTarget_lbfgs(loader.dofInfo);
	return out
end

-- prev_pose will be updated to be the next pose.
function fc.solveIK(mSolverInfo, prev_pose, dotpose, desired_pose, comdof, footdof, effWeights, config) 
	-- V: world momentum-mapping velocity error (relative to prev_pose+dotpose*dt)
	-- when V is zero, MM term has no effects
	local V=Liegroup.se3(comdof:toVector3(7), comdof:toVector3(10))
	
	RE.output2('V0', V.w, V.v)

	local hasCOM=1
	local hasMM=1
	local hasPoseCon=1
	local useEffYcon=1
	local wCOMy=0.0
	local wFullVel=0.01
	local wFullVelPose=0.001
	local wFullVelPose2=0.005
	local wMM=0.1
	local frameRate=30
	if config then
		wCOMy=config.wCOMy or 0.0
		if config.wFullVel then wFullVel=config.wFullVel end
		if config.wFullVelPose then wFullVelPose=config.wFullVelPose wFullVelPose2=config.wFullVelPose*5 end
		if config.wFullVelPose2 then wFullVelPose2=config.wFullVelPose2 end
		if config.wMM then wMM=config.wMM end
		if config.hasCOM then hasCOM=config.hasCOM end
		if config.hasMM then hasMM=config.hasMM end
		if config.hasPoseCon then hasPoseCon=config.hasPoseCon end
		if config.useEffYcon then useEffYcon=config.useEffYcon end
		if config.frameRate then frameRate=config.frameRate end
	else
		config={}
	end

	local comtf=MotionDOF.rootTransformation(comdof)


	local pose=prev_pose

	local numCon=mSolverInfo.numCon
	local footPos=vector3N (numCon);

	for i=0, numCon-1 do
		footPos(i):assign(footdof:toVector3(3*i))
	end

	local mIK=mSolverInfo.solver
	local mEffectors=mSolverInfo.effectors


	--
	--local prev_roottf=MotionDOF.rootTransformation(pose)
	--local toLocal=prev_roottf:inverse()
	local toLocal=MotionDOF.rootTransformation(comdof):inverse()

	if not config.noPlannarProjection then
		toLocal.translation.y=0
		toLocal.rotation:assign(toLocal.rotation:rotationY())
	end

	local useHead=config.useHead or 1
	local hasVelCon=0
	if config.vel_con then
		hasVelCon=hasVelCon+#config.vel_con
	end

	if not config.v2_max then
		config.v2_max=math.max(V.v:length(), V.w:length(), 10)
	end
	if not config.effWeightsY then
		config.effWeightsY=0.1
	end
	local v2newpose=MotionDOF.calcVelocity(prev_pose, desired_pose, frameRate)
	v2newpose:clamp(config.v2_max)
	mIK:_changeNumEffectors(numCon)
	if effWeights then
	else
		effWeights=vectorn(numCon)
		effWeights:setAllValue(1.0)
	end
	for i=0, numCon-1 do mIK:_setEffectorWeight(i, math.pow(effWeights(i),config.effwPower or 2)*config.effWeightsY) end
	mIK:_changeNumConstraints(hasCOM+hasMM+useHead+hasPoseCon*3+useEffYcon+hasVelCon)

	local COM=comtf.translation
	if hasCOM==1 then
		mIK:_setCOMConstraint(0, toLocal*COM, 1,wCOMy,1)
	end
	--if g_dbgdbg then dbg.console() end
	if hasMM==1 then
		-- because (initial pose)==pose==prev_pose+dotpose
		-- MM con needs to consider only the remaining V (in global)
		V:Ad_ori(toLocal.rotation)
		local dt=1/frameRate
		--local dt=1
		RE.output2('V', V.w, V.v, toLocal.rotation)
		mIK:_setMomentumConstraint(hasCOM, V.w*dt, V.v*dt, wMM)
	end
	mIK:setParam('damping_weight', 0,0)
	mIK:setParam('root_damping_weight', 0.01,1)

	if false then
		-- 모션 품질 나빠짐.
		-- clamp dotpose
		local thr=math.rad(10)
		for i=7, dotpose:size()-1 do
			if prev_pose(i)> desired_pose(i)+thr and dotpose(i)>0  then
				dotpose:set(i,0)
			end
			if prev_pose(i)< desired_pose(i)-thr and dotpose(i)<0  then
				dotpose:set(i,0)
			end
		end
	end
	local kneeDOFs=mSolverInfo.kneeDOFs
	if kneeDOFs then
		-- knee damping
		local thr=0
		for ii=0, kneeDOFs:size()-1 do
			i=kneeDOFs(ii) 

			if prev_pose(i)< thr and dotpose(i)<0  then
				dotpose:set(i,0)
			end
		end
	end

	local nextPose1=MotionDOF.integrate(prev_pose, dotpose, frameRate)
	local nextPose2=MotionDOF.integrate(prev_pose, v2newpose, frameRate)
	if false then
		if not g_debugskin then
			g_debugskin=RE.createVRMLskin(g_info.loader, false)
			g_debugskin:setScale(100,100,100)
			g_debugskin:setTranslation(100,0,0)
			g_debugskin2=RE.createVRMLskin(g_info.loader, false)
			g_debugskin2:setScale(100,100,100)
			g_debugskin2:setTranslation(200,0,0)
			g_debugskin3=RE.createVRMLskin(g_info.loader, false)
			g_debugskin3:setScale(100,100,100)
			g_debugskin3:setTranslation(300,0,0)
		end
		g_debugskin:setPoseDOF(nextPose1)
		g_debugskin2:setPoseDOF(prev_pose)
		g_debugskin3:setPoseDOF(desired_pose)

	end

	--dbg.namedDraw('Axes', prev_pose:toTransf(0), 'prev_pose', 100,0.5)
	--dbg.namedDraw('Axes', nextPose1:toTransf(0), 'nextpose1', 100,0.5)
	--dbg.namedDraw('Axes', nextPose2:toTransf(0), 'nextpose2', 100,0.5)

	-- IK initial solution
	pose:assign(nextPose1)

	local tf=transf()
	local tf1=nextPose1:toTransf(0)
	local tf2=nextPose2:toTransf(0)
	tf:interpolate(0.9, tf1, tf2)
	pose:setTransf(0, tf)

	local  headPos, headBone
	if useHead==1 then
		local loader=mSolverInfo.loader
		--local headRefPose=loader.dofInfo:blendPose( nextPose1, nextPose2, 0.1)
		--loader:setPoseDOF(headRefPose)
		headBone=loader:getBoneByName(input.head[1])
		--headOri=headBone:getFrame().rotation:copy()
		--local COMtoHead=headBone:getFrame()*input.head[2]- loader:calcCOM()
		local COMtf=MotionDOF.rootTransformation(comdof)
		headPos=COMtf*input.head[3]
		--dbg.draw('Sphere', headPos*100, 'head')
	end
	MotionDOF.setRootTransformation(pose, toLocal*MotionDOF.rootTransformation(pose))
	MotionDOF.setRootTransformation(nextPose1, toLocal*MotionDOF.rootTransformation(nextPose1))
	MotionDOF.setRootTransformation(nextPose2, toLocal*MotionDOF.rootTransformation(nextPose2))

	if hasPoseCon==1 then
		--for i=1, mMot.loader:numBone()-1 do print(i,mMot.loader:bone(i):name()) end
		mIK:_setPoseConstraint(hasCOM+hasMM, nextPose1, wFullVel, 2)  -- fullbody velocity constraint
		mIK:_setPoseConstraint(hasCOM+hasMM+1, nextPose2, wFullVelPose, 2)  -- fullbody poseconstraint
		if not input.lowerbody then
			input.lowerbody={2,10000}
		end
		mIK:_setPoseConstraint(hasCOM+hasMM+2, nextPose2, wFullVelPose2, input.lowerbody[1],input.lowerbody[2] ) -- lowerbody pose constraint
	end
	if config.debugDraw then
		for c=0,numCon-1 do
			dbg.namedDraw('Sphere', footPos(c)*100, 'feet'..c)
		end
	end
	for i=0,numCon-1 do
		mIK:_setEffector(i, mEffectors(i).bone, mEffectors(i).localpos)
		footPos(i):assign(toLocal*footPos(i))
	end
	if useHead==1 then
		local i=numCon
		mIK:_setPositionConstraint(hasCOM+hasMM+hasPoseCon*3, headBone, input.head[2], toLocal*headPos, 1,config.wHead_y or 0,config.wHead_z or 0.1 );
	end

	if useEffYcon==1 then
		local ew=effWeights:copy()
		for i=0,ew:size()-1 do ew:set(i, math.pow(ew(i),config.effwPower or 2)) end

		mIK:_setEffectorYConstraint(hasCOM+hasMM+useHead+hasPoseCon*3, 1.0, ew)
	end

	if config.vel_con then
		for i,v in ipairs(config.vel_con) do
			local loader=mSolverInfo.loader
			local bone=loader:getBoneByName(v[1][1])
			local lpos=v[1][2]
			local gpos=v[2]
			local offset=v[3]
			local normal=offset:copy()
			normal:normalize()
			mIK:_setNormalConstraint(hasCOM+hasMM+useHead+hasPoseCon*3+useEffYcon+i-1, bone, lpos, toLocal.rotation*normal, toLocal*(gpos+offset*1/frameRate))
		end
	end

	mIK:_effectorUpdated()
	mIK:IKsolve(pose, footPos)



	MotionDOF.setRootTransformation(pose, toLocal:inverse()*MotionDOF.rootTransformation(pose))
	assert(prev_pose==pose)

	--MotionDOF.setRootTransformation(nextPose1, toLocal:inverse()*MotionDOF.rootTransformation(nextPose1)) pose:assign(nextPose1)
	--MotionDOF.setRootTransformation(nextPose2, toLocal:inverse()*MotionDOF.rootTransformation(nextPose2)) pose:assign(nextPose2)
end
function fc.solveIK_postprocess(mSolverInfo, prev_pose, comdof, footdof, effWeights, config) 
	local pose=prev_pose

	local numCon=mSolverInfo.numCon
	local footPos=vector3N (numCon);

	for i=0, numCon-1 do
		footPos(i):assign(footdof:toVector3(3*i))
	end

	local mIK=mSolverInfo.solver
	local mEffectors=mSolverInfo.effectors
	--local prev_roottf=MotionDOF.rootTransformation(pose)
	--local toLocal=prev_roottf:inverse()
	local toLocal=MotionDOF.rootTransformation(comdof):inverse()
	toLocal.translation.y=0
	toLocal.rotation:assign(toLocal.rotation:rotationY())


	local hasCOM=1
	local hasMM=0
	local wCOMy=0.0
	local wMM=0.1
	local frameRate=30
	if config then
		wCOMy=config.wCOMy or 0.0
		if config.wMM then wMM=config.wMM end
		if config.hasCOM then hasCOM=config.hasCOM end
		if config.hasMM then hasMM=config.hasMM end
		if config.frameRate then frameRate=config.frameRate end
	else
		config={}
	end
	local hasVelCon=0
	if config.vel_con then
		hasVelCon=hasVelCon+#config.vel_con
	end


	local useHead=config.useHead or 1

	if not config.effWeightsY then
		config.effWeightsY=0.1
	end
	mIK:_changeNumEffectors(numCon)
	if effWeights then
	else
		effWeights=vectorn(numCon)
		effWeights:setAllValue(1.0)
	end
	for i=0, numCon-1 do mIK:_setEffectorWeight(i, math.pow(effWeights(i),2)*config.effWeightsY) end
	mIK:_changeNumConstraints(hasCOM+hasMM+useHead+1+hasVelCon)

	local COM
	do
		local loader=mSolverInfo.loader
		loader:setPoseDOF(prev_pose)
		COM=loader:calcCOM()
	end

	if hasCOM==1 then
		mIK:_setCOMConstraint(0, toLocal*COM, 1,wCOMy,1)
	end
	--if g_dbgdbg then dbg.console() end
	if hasMM==1 then
		mIK:_setMomentumConstraint(hasCOM, vector3(0,0,0), vector3(0,0,0), wMM)
	end
	mIK:setParam('damping_weight', 0.01,0.01)

	local  headPos, headBone
	if useHead==1 then
		local loader=mSolverInfo.loader
		--local headRefPose=loader.dofInfo:blendPose( nextPose1, nextPose2, 0.1)
		--loader:setPoseDOF(headRefPose)
		headBone=loader:getBoneByName(input.head[1])
		headPos=headBone:getFrame()*input.head[2]
	end
	MotionDOF.setRootTransformation(pose, toLocal*MotionDOF.rootTransformation(pose))

	for i=0,numCon-1 do
		mIK:_setEffector(i, mEffectors(i).bone, mEffectors(i).localpos)
		footPos(i):assign(toLocal*footPos(i))
	end
	if useHead==1 then
		local i=numCon
		mIK:_setPositionConstraint(hasCOM+hasMM, headBone, input.head[2], toLocal*headPos, 1,config.wHead_y or 0,0.1 );
	end
	local ew=effWeights:copy()
	for i=0,ew:size()-1 do ew:set(i, math.pow(ew(i),2)) end
	
	mIK:_setEffectorYConstraint(hasCOM+hasMM+useHead, 1.0, ew)

	if config.vel_con then
		for i,v in ipairs(config.vel_con) do
			local loader=mSolverInfo.loader
			local bone=loader:getBoneByName(v[1][1])
			local lpos=v[1][2]
			local gpos=v[2]
			local offset=v[3]
			local normal=offset:copy()
			normal:normalize()
			mIK:_setNormalConstraint(hasCOM+hasMM+1+i, bone, lpos, toLocal.rotation*normal, toLocal*(gpos+offset*1/frameRate))
		end
	end

	mIK:_effectorUpdated()
	mIK:IKsolve(pose, footPos)

	MotionDOF.setRootTransformation(pose, toLocal:inverse()*MotionDOF.rootTransformation(pose))
	assert(prev_pose==pose)
end

-- input: loader, mot, con, feet_config={toe=vector3(0,-0.05, 0.14), heel=vector3(0,-0.10, -0.06)} , option={}
-- output: self.motionDOF, self.con
function fc.prepareMotionsForSim(loader, mot, con, initial_height, feet_config, option) 
	local self={}
	self.motionDOF=mot:copy()

	assert(loader)
	assert(mot)

	local mMotionDOF=self.motionDOF
	for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i,1, mMotionDOF:matView()(i,1)+initial_height)
	end


	self.con=con
	self.conWeight={}
	for ilimb=1, 2 do
		local nf=self.con[ilimb]:size()
		self.conWeight[ilimb]=CT.ones(nf)
		local segments=intIntervals()
		segments:runLengthEncode(self.con[ilimb])
		for iseg=0, segments:numInterval()-1 do
			local startSwing=0
			local endSwing=0
			if iseg==segments:numInterval()-1 then
				startSwing=segments:endI(iseg)
				endSwing=segments:startI(0)+nf-1
			else
				startSwing=segments:endI(iseg)
				endSwing=segments:startI(iseg+1)
			end
			for i=startSwing, endSwing-1 do
				local w=sop.map(i, startSwing-2, endSwing, -1, 1) -- w decreases early for better motion style.
				local wmap=option.conWeightMap or function(w, i, startSwing, endSwing) return math.pow(w,4) end
				if i<nf then
					self.conWeight[ilimb]:set(i, wmap(w, i, startSwing, endSwing))
				else
					self.conWeight[ilimb]:set(i-nf, wmap(w, i, startSwing, endSwing))
				end
			end
		end
	end
	--fc.removeFeetSliding(self.con, feet_config, loader, self.motionDOF_fullbody)
	return self
end

local function diffPose(a, b)
	local pose= b-a
	local qd=quater()
	qd:difference(a:toQuater(3), b:toQuater(3))
	pose:setQuater(3, qd)
	return pose
end
local function addPose(a, b)
	local pose= a+b
	local q=b:toQuater(3)*a:toQuater(3)
	pose:setQuater(3, q)
	return pose
end
local function scalePose(a,s)
	local pose= a*s
	local q=a:toQuater(3)
	q:scale(s)
	pose:setQuater(3, q)
	return pose
end
fc.diffPose=diffPose
fc.addPose=addPose
fc.scalePose=scalePose
fc.blendPose=blendPose
return fc
