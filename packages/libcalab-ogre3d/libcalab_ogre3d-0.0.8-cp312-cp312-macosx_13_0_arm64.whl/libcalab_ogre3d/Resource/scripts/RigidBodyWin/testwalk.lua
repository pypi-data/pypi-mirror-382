require("config")
require("module")
require("common")

-- mMotion의 현재 재생중인 프레임 뒤로 적어도 lookAhead만큼의 여분이 있음.
-- lookAhead는 가장 짧은 세그먼트의 길이보다 작아야함.
lookAhead=20
-- 동작 stitch시 접합점 기준으로 lookTail만큼 변형될 수 있음.
lookTail=20
gCount=0

function turn(amount)
	local currFrame=math.round(mTime*120)-mDelta -- 프레임단위
	print(currFrame)
	local edit=MotionUtil.RetargetOnline2D(mMotion, currFrame)
	local turnDuration=lookAhead
	edit:adjust(currFrame+turnDuration-1, math.rad(amount))
	--edit:adjustSafe(currFrame+turnDuration-1, math.rad(amount))
end

function GetLoader(Loader)


end

function ctor()
	this:create("Button", "lturn", "left turn");
	this:create("Button", "rturn", "right turn");
	this:create("Value_Slider", "slidery", "slidery");
	this:widget(0):sliderRange(0,0.5);
	this:widget(0):sliderValue(0.1);
	this:create("Check_Button", "attach camera", "attach camera")
	this:widget(0):buttonShortcut("FL_ALT+c")
	this:create("Check_Button", "draw forward", "draw forward")
	this:findWidget("draw forward"):checkButtonValue(true)
	this:create("Check_Button", "stop", "stop")
	this:updateLayout();

	mCameraInfo=nil
	mLoader=MainLib.VRMLloader ("../Resource/motion/gymnist/gymnist.wrl")

	mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo, '../Resource/motion/gymnist/gymnist.dof')
	mMotionDOF=mMotionDOFcontainer.mot

	-- in meter scale
	for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i, 1, mMotionDOF:matView()(i,1)+0.07)
	end
	mMotionDOF_delta=MotionDOF(mMotionDOF)
	mMotionDOF_delta:convertToDeltaRep();

	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, false);
	mSkin:scale(100,100,100); -- motion data is in meter unit while visualization uses cm unit.
	mSkin:setPoseDOF(mMotionDOF:row(0));

	mGraph={ 
		start={644, 821, next='walk'}, 
		walk={821, 972, next='walk'},
		turn={972,1500, next='turn'}
	}

	for key, seg in pairs(mGraph) do
		--print(key)
		--printTable(seg)
		seg.mot=mMotionDOF:range(seg[1], seg[2]):copy()
		seg.dmot=mMotionDOF_delta:range(seg[1], seg[2]):copy()
		--print('after')
		--printTable(seg)
	end
	
	mCurrSeg=mGraph.start
	mMotion=mCurrSeg.mot
	mDelta=0
	mTime=0
	--mNewMotion=MotionDOF(mLoader.dofInfo)
	--mNewMotion:stitch(mGraph.start.mot, mGraph.walk.mot)
	--mNeMotion2=MotionDOF(mLoader.dofInfo)
	--mNewMotion2:stitch(mNewMotion, mGraph.walk.mot)

	--mSkin:applyMotionDOF(mNewMotion2)
	--RE.motionPanel():motionWin():addSkin(mSkin)
	
	--print('ctor')
	--testData=readText()
end

function frameMove(fElapsedTime)
	mTime=mTime+fElapsedTime
			--print('mDelta[[[[[['..mDelta)
	--print(mTime)
	local currFrame=math.round(mTime*120) -- 프레임단위
			--print('currFrame[[[[[['..currFrame)
	local preFrameSet=3
	if mMotion:numFrames()+mDelta<currFrame+lookAhead then
		local prevMotion=mMotion
		local nextSeg=mGraph[mCurrSeg.next].mot
		local nextSeg_delta=mGraph[mCurrSeg.next].dmot
			mMotion=MotionDOF(mLoader.dofInfo)
		if false then
			-- this works but is slow due to large # of optimization variables.
			mMotion:changeLength(prevMotion:length()+nextSeg:length())
			mMotion:range(0, prevMotion:numFrames()-lookAhead):assign( prevMotion:range(0, prevMotion:numFrames()-lookAhead))
			mMotion:range(prevMotion:numFrames()-lookAhead, mMotion:numFrames()):stitch(
			prevMotion:range(prevMotion:numFrames()-lookAhead, prevMotion:numFrames()),
			nextSeg)
		else
		

			--print('lookAhead[[[[[['..lookAhead)
			--print('lookTail[[[[[['..lookTail)
			
			local prevLen=prevMotion:length()
			local newLen=prevLen+nextSeg:length()
			local newActualLength=lookAhead+preFrameSet+nextSeg:length()
			--print('newActualLength[[[[[[[[['..newActualLength)
			mDelta=mDelta+newLen-newActualLength
			--numFrames = length + 1
			--데이터 크기 변경 : 23프레임 + 다음 모션
			mMotion:changeLength(newActualLength)
			--데이터 복사 b->a a:range(시작,끝):assign(b:range(시작,끝)
			mMotion:range(0, preFrameSet):assign( prevMotion:range(prevLen+1-lookAhead-preFrameSet, prevLen+1-lookAhead))
			--데이터 합치기 c=a+b  c:range(start,end):stitch(a,b)  
			mMotion:range(preFrameSet,preFrameSet+lookAhead+lookTail):stitch(
			prevMotion:range(prevMotion:length()-lookAhead, prevMotion:numFrames()),
			nextSeg:range(0,lookTail))
			local delta_copy=nextSeg_delta:range(lookTail-1, nextSeg:numFrames()):copy()
			-- stitch된 부분의 마지막 프레임의 rootConfiguration 의 2d성분을 받아옴. (x,z위치와 수직방향 오리엔테이션)
			local startTransformation2D=mMotion:rootTransformation(preFrameSet+lookAhead+lookTail-1):encode2D()
			-- delta 형식을 일반 동작데이타 형식으로 변경. 이때 시작 configuration에서 시작하도록 함.
			delta_copy:reconstructData(startTransformation2D)
			mMotion:range(preFrameSet+lookAhead+lookTail,newActualLength+1):assign( delta_copy:range(1, delta_copy:numFrames()))
		end


	end

--[[	
	if mCameraInfo and this:findWidget("attach camera"):checkButtonValue() then
		local currFrame=math.round(mTime*120)-mDelta -- 프레임단위
		local curPos=mMotion:row(currFrame):toVector3(0)*100
		local vpos=mCameraInfo.vpos+curPos
		local vat=mCameraInfo.vat+curPos
		print (currFrame, curPos, vat)

		RE.viewpoint().vpos:assign(vpos)
		RE.viewpoint().vat:assign(vat)
		RE.viewpoint():update()
	end
	if this:findWidget("draw forward"):checkButtonValue() then
		local currFrame=math.round(mTime*120)-mDelta -- 프레임단위
		local curPos=mMotion:row(currFrame):toVector3(0)*100 -- meter to cm
		local curOri=mMotion:row(currFrame):toQuater(3):rotationY()
		local curFrontDir=rotate(vector3(0,0,1), curOri) -- z axis is the local front (usually)
		

		--dbg.draw('Line1', changePos, changePos*100, "front direction", "solidblue")	
		--print(type(changePos))
		--dbg.draw('Sphere',curPos, 'cc1','red',20)
	end
	if this:findWidget("stop"):checkButtonValue() then
		dbg.console()
	end]]--
	mSkin:setPoseDOF(mMotion:row(currFrame-mDelta))
	--turn(50)
	
	gCount=gCount+1 
end

currCursorPos=vector3(0,0,0)
function onCallback(w, userData)
   if w:id()=="button1" then
	   print("button1\n");
   elseif w:id()=="button2" then
	   print("button2\n");
   elseif w:id()=="attach camera" then

	   local currFrame=math.round(mTime*120)-mDelta -- 프레임단위
	   local curPos=mMotion:row(currFrame):toVector3(0)*100
	   mCameraInfo={}
	   mCameraInfo.vpos=RE.viewpoint().vpos-curPos
	   mCameraInfo.vat=RE.viewpoint().vat-curPos
   elseif w:id()=="sliderx"or w:id()=="slidery" then
   elseif w:id()=="lturn" then
	   turn(50)
   elseif w:id()=="rturn" then
	   turn(-50)
	   --turn(-10)
   end
   --print('oncallback')
end

function dtor()
		print('dtor')
end
function dbgDraw(name, pos, color)
	color = color or 'blue'
	dbg._namedDraw('Sphere', pos, name, color, 5)
end

function handleRendererEvent(ev,button,x,y)
	if ev =="PUSH" or 
	ev=="MOVE" or
	ev=="DRAG" or
	ev=="RELEASE" then
		local currFrame=math.round(mTime*120)-mDelta -- 프레임단위
		local curPos=mMotion:row(currFrame):toVector3(0)*100 -- meter to cm
		local curOri=mMotion:row(currFrame):toQuater(3):rotationY()
		local curFrontDir=rotate(vector3(0,0,1), curOri)
		currCursorPos=RE.FltkRenderer():screenToWorldXZPlane(x,y);
		print(currCursorPos)
		dbgDraw("cc",currCursorPos,'blue')

		local changepos=vector3(0,0,0)
		changepos=currCursorPos-curPos

		changepos:normalize()

		dbg.draw('Sphere',changepos*100, 'cc1','red',10)

	

	end
		
	return 0
end


function readText()
	local maxText = 5000000;
	out=vectorn()
	local input = util.readFile('testRec.txt')
	structIn = string.lines(input) 
	for i=1,maxText do
		print('i:',i)
		if structIn[i]=='' then
			break;
		else
			out:resize(i);
			out:set(i-1,structIn[i])
		end
	end
	return out
end
