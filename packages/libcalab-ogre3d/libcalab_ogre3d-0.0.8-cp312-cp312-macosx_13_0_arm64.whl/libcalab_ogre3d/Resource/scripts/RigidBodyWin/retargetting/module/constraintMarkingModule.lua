
ConTypes={ 
	GROUND_CONTACT=1,
	RELATIVE_POSITION=2,
}
function ConTypes.markTarget(loader, motionDOFcontainer, target, constraint, drawSignals)
	if constraint.conType==ConTypes.RELATIVE_POSITION then
		local mot=motionDOFcontainer.mot
		local conL=boolN(mot:numFrames())
		local con=constraint
		conL:setAllValue(false)
		local pos=MotionUtil.getPositions(loader, mot, con.bones, con.localPos)
		target.con=conL
		target.pos=pos
	else
		local con, toePos, heelPos, jointPos = ConTypes.mark(loader, motionDOFcontainer, constraint, drawSignals)
		target.con=con
		target.toePos=toePos
		target.heelPos=heelPos
		target.jointPos=jointPos
	end
end

function ConTypes.mark(loader, motionDOFcontainer, config, drawSignals)

	assert(config.conType)
	-- index가 1이면 왼발, 2이면 오른발
	local mot=motionDOFcontainer.mot

	
	local thr_speed=config.thr_speed
	local toelimitL = config.toelimit
	local heellimitL = config.heellimit

	local pos=MotionUtil.getPositions(loader, mot, 
	{config.toes, config.heel, config.heel}, 
	{config.toes_lpos, config.heel_lpos, vector3(0,0,0)})

	local toePosL=pos[1]
	local anklePosL=pos[2]

	local discontinuity = motionDOFcontainer.discontinuity
	local frame_rate=loader.dofInfo:frameRate()
	--matrixn:derivative( frame_rate, discontinuity)
	toeVelL=toePosL:derivative( frame_rate, discontinuity)

	if not config.filter_size then 
		print("giving up automatically marking constraints!") 
		local conL=boolN(toePosL:size())
		conL:setAllValue(false)
		return conL, toePosL, anklePosL, pos[3]
	end
	ankleVelL=anklePosL:derivative( frame_rate, discontinuity)

	math.filter(toeVelL, config.filter_size)
	math.filter(ankleVelL, config.filter_size)

	toespeedL=vectorn(toeVelL:rows())
	heelspeedL=vectorn(ankleVelL:rows())
	for i=0, toeVelL:rows()-1 do
		toespeedL:set(i, toeVelL:row(i):toVector3():length())
	end
	for i=0, ankleVelL:rows()-1 do 
		heelspeedL:set(i, ankleVelL:row(i):toVector3():length())
	end
	local velRows = toeVelL:rows()
	local conL=boolN(velRows)
	conL:setAllValue(false)

	--constraint deciding
	for i=0, toeVelL:rows()-1 do
		if toespeedL(i) < thr_speed and toePosL(i,1) < toelimitL 
			or heelspeedL(i) < thr_speed and 
			anklePosL(i,1) < heellimitL then

			conL:set(i, true)
		end
	end

	if drawSignals then
		Imp.ChangeChartPrecision(70);
		local pSignalL=Imp.DrawChart(toespeedL:row(), Imp.LINE_CHART, 0, math.min(config.thr_speed*2, 1), config.thr_speed);
		RE.motionPanel():scrollPanel():addPanel(pSignalL)
		RE.motionPanel():scrollPanel():setLabel("toespeed")

		local pSignalL=Imp.DrawChart(heelspeedL:row(), Imp.LINE_CHART, 0, math.min(config.thr_speed*2, 1), config.thr_speed);
		RE.motionPanel():scrollPanel():addPanel(pSignalL)
		RE.motionPanel():scrollPanel():setLabel("heelspeed")

		local pSignalL=Imp.DrawChart(toePosL:column(1):copy():row(), Imp.LINE_CHART, 0, toelimitL*2, toelimitL);
		RE.motionPanel():scrollPanel():addPanel(pSignalL)
		RE.motionPanel():scrollPanel():setLabel("toeheight")

		local pSignalL=Imp.DrawChart(anklePosL:column(1):copy():row(), Imp.LINE_CHART, 0, heellimitL*2, heellimitL);
		RE.motionPanel():scrollPanel():addPanel(pSignalL)
		RE.motionPanel():scrollPanel():setLabel("ankleheight")
	end

	Imp.DefaultPrecision();
	return conL, toePosL, anklePosL, pos[3]
end
function conToImportance(con, spprtRegion)
	local importance=vectorn(con:size())
	importance:setAllValue(0)
	local conInterval=intIntervals();
	conInterval:runLengthEncode(con)
	local numConGrp=conInterval:size();

	if numConGrp==0 then
		return importance
	end
	for grp=0, numConGrp -1 do
		importance:range(conInterval:startI(grp), conInterval:endI(grp)):setAllValue(1)
	end

	for grp=0, numConGrp do
		local startF
		local endF
		if grp==0 then
			startF=math.max(conInterval:startI(grp)-spprtRegion,0)
			endF=conInterval:startI(grp)
			local s=sop.map(endF-startF, 0, spprtRegion, 1, 0)
			importance:range(startF, endF):smoothTransition(s, 1, endF-startF)

		elseif grp==numConGrp then
			startF=conInterval:endI(grp-1)
			endF=math.min(startF+spprtRegion, con:size())
			local e=sop.map(endF-startF, 0, spprtRegion, 1, 0)
			importance:range(startF, endF):smoothTransition(1, e, endF-startF)
		else
			startF=conInterval:endI(grp-1)
			endF=conInterval:startI(grp)

			if endF-startF > spprtRegion*2 then
				importance:range(startF, startF+spprtRegion):smoothTransition(1, 0, spprtRegion)
				importance:range(endF-spprtRegion, endF):smoothTransition(0, 1, spprtRegion)
			else
				local mid=math.floor((startF+endF)/2)
				local m=sop.map (mid-startF, 0, spprtRegion, 1, 0)
				importance:range(startF, mid):smoothTransition(1, m, mid-startF)
				importance:range(mid, endF):smoothTransition(m, 1, endF-mid)
			end
		end
	end

	if not already_draw_chart then
		already_draw_chart=true
		Imp.ChangeChartPrecision(50)
		local pSignal=Imp.DrawChart(importance:row(), Imp.LINE_CHART)
		pSignal:Save("signal.bmp");
		RE.motionPanel():scrollPanel():addPanel("signal.bmp");
	end
	return importance
end
