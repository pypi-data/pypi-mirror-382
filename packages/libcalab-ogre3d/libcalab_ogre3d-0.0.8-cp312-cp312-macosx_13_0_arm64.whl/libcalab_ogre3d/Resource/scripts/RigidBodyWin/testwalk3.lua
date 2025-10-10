require("config")
require("module")
require("common")

package.projectPath='../Samples/classification/'
package.path=package.path..";../Samples/classification/lua/?.lua" --;"..package.path
require('control/SDRE')
debugVis=true 

-- mMotion의 현재 재생중인 프레임 뒤로 적어도 lookAhead만큼의 여분이 있음.
-- lookAhead는 가장 짧은 세그먼트의 길이보다 작아야함.
lookAhead=12
-- 동작 stitch시 접합점 기준으로 lookTail만큼 변형될 수 있음.
lookTail=12

-- left, right turn function
function turn(amount)
	local currFrame=math.round(mTime*100)-mDelta -- 프레임단위
--	print(currFrame)
--	dbg.console();
	local edit=MotionUtil.RetargetOnline2D(mMotion, currFrame)
	local turnDuration=lookAhead
	edit:adjust(currFrame+turnDuration-1, math.rad(amount))
end

function ctor()
	--ojbect path 
	bvh_files=string.lines([[
	2/gf_body2-1.bvh
	2/table.bvh
	]])
	bvh_files_prefix='../Resource/mocap_manipulation/bvh_files/gf_0515/'
	
	obj_files=string.lines([[
	cup.obj
	table.obj
	]]) 
	obj_files_prefix='../Resource/mocap_manipulation/obj_files/gf/'

	--bvh trimstring -> array
	array.foreach(bvh_files, string.trimSpaces)
	array.foreach(obj_files, string.trimSpaces)

	--menu create
	this:create("Choice", "menu")
	this:widget(0):menuSize(#bvh_files)
	for i,v in ipairs(bvh_files) do
		this:widget(0):menuItem(i-1, v)
	end
	this:widget(0):menuValue(0)

	mEventReceiver=EVR()

	this:create("Value_Slider", "sliderx", "sliderx");
	this:widget(0):sliderRange(-10,10);
	this:widget(0):sliderValue(0);
	this:create("Value_Slider", "slidery", "slidery");
	this:widget(0):sliderRange(-10,10);
	this:widget(0):sliderValue(0);
	this:create("Value_Slider", "sliderz", "sliderz");
	this:widget(0):sliderRange(-10,10);
	this:widget(0):sliderValue(0);

	this:create("Check_Button", "turn", "turn")

	this:updateLayout();

	local bvh_file=bvh_files_prefix..'2/gf_skel2-1.bvh'
	local wrl_file=bvh_files_prefix..'2/gf_skel2-1.wrl'

	mCameraInfo=nil
	mLoader=MainLib.VRMLloader ("../Resource/mocap_manipulation/bvh_files/gf_0515/2/gf_skel2-1.wrl")
	mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo, '../Resource/mocap_manipulation/bvh_files/gf_0515/2/gf_skel2-1.dof')
	mMotionDOF=mMotionDOFcontainer.mot

	-- in meter scale
	for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i, 1, mMotionDOF:matView()(i,1)+0.07)
	end
	mMotionDOF_delta=MotionDOF(mMotionDOF)
	mMotionDOF_delta:convertToDeltaRep();

	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, false);
	mSkin:scale(1,1,1); -- motion data is in meter unit while visualization uses cm unit.
	mSkin:setPoseDOF(mMotionDOF:row(0));

	-- motion graph
	mGraph={ 
		start={0, 180, next='walk1'}, 
		walk1={180, 193, next='walk2'},
		walk2={193, 206, next='walk3'},
		walk3={206, 219, next='walk4'},
		walk4={219, 232, next='walk5'},
		walk5={232, 245, next='walk6'},
		walk6={245, 258, next='walk7'},	
		walk7={258, 271, next='walk8'},
		walk8={271, 284, next='walk9'},
		walk9={284, 297, next='walk10'},
		walk10={297, 310, next='walk11'},
		walk11={310, 323, next='walk1'},
		stop = {425, 438, next='stop'},
		cont = {438, 1950, next='cont'}
	}

	for key, seg in pairs(mGraph) do
		--print(key)
		--printTable(seg)
		seg.mot=mMotionDOF:range(seg[1], seg[2]):copy()
		seg.dmot=mMotionDOF_delta:range(seg[1], seg[2]):copy()
		--print('after')
		--printTable(seg)
	end

	do -- set viewpoint
		RE.viewpoint():setFOVy(20)
		local vpos=vector3(1000, 300,-100)
		local vat=vector3(-70, 100, -100)
		RE.viewpoint().vpos:assign(vat+(vpos-vat)*1.5)
		RE.viewpoint().vat:assign(vat)
		RE.viewpoint():update()
		--RE.renderer():fixedTimeStep(false)   
	end
	-- object variable
	g_skels={}
	g_skins={}
	g_motions2={}
	dis_table = 0
	-- object load
	objShow(1)
	objShow(2)
	flag = 0;
	temp_curr=0;
	temp_cen=0;
	--initialize motion
	mCurrSeg=mGraph.start
	mMotion=mCurrSeg.mot
	mDelta=0
	mTime=0
	rwalk_f=1
	lwalk_f=0
	rstop_f=0
	stop_f=0

	prevLen = 0

	obj_flag=0
	cFrame = 0
	step_cnt = 0

	temp_f1=0
	temp_f2=0
	temp_f3=0
	i=0
	table_center = g_motions2[2]:row(0)(0)

	sec_start = 3600
	print('ctor')
end

function Sleep(sec)
	local begin = os.clock()
	while os.clock() - begin < sec do end
end

function objShow(menuValue)
		local m=menuValue
		local bvh_file=bvh_files_prefix..bvh_files[m]
		local wrl_file=string.sub(bvh_file, 1, -4)..'wrl'
		local fn=os.filename(string.sub(bvh_file,1,-5))
		-- BVH file
		local skel=RE.createMotionLoader(bvh_file, bvh_file)
		-- WRL file
		g_skels[m]=MainLib.VRMLloader(wrl_file);
		g_skins[m]=RE.createVRMLskin(g_skels[m], false)
		-- MotionDOF (for WRL file) can be generated from the BVH file
		g_motions2[m]=convertMotionToMotDOF(skel, skel.mMotion, g_skels[m])
		
		local xx = 0
		local yy = 0
		local zz = 0
		for i=0,1952 do
		g_motions2[m]:row(i):setVec3(0, g_motions2[m]:row(i):toVector3()+vector3(xx,yy,zz))
		end
		g_skins[m]:setPoseDOF(g_motions2[m]:row(0))
end

function frameMove(fElapsedTime)
	if sec_start == 1 then
	mTime=mTime+fElapsedTime
	--print(mTime)
	local currFrame=math.round(mTime*100) -- 프레임단위
	local preFrameSet=3
	--print(currFrame);
	if mMotion:numFrames()+mDelta<currFrame+lookAhead  then
		--print(flag)
		if flag == 0 then
			sec_start = 0
		elseif flag == 1 then
			sec_start = 0
			mCurrSeg = mGraph.walk1
		elseif flag == 2 then
			mCurrSeg = mGraph.walk2
		elseif flag == 3 then
			mCurrSeg = mGraph.walk3
		elseif flag == 4 then
			mCurrSeg = mGraph.walk4
		elseif flag == 5 then
			mCurrSeg = mGraph.walk5
		elseif flag == 6 then
			mCurrSeg = mGraph.walk6
		elseif flag == 7 then
			mCurrSeg = mGraph.walk7
		elseif flag == 8 then
			mCurrSeg = mGraph.walk8
		elseif flag == 9 then
			mCurrSeg = mGraph.walk9
		elseif flag == 10 then
			mCurrSeg = mGraph.walk10
		elseif flag == 11 then 
			mCurrSeg = mGraph.walk11
		end
		--constraint table distance
		if dis_table < 70 then
			mCurrSeg = mGraph.stop
		end
	--	print(temp_cen)
	--	print(dis_table)
	--	print(flag)
		if temp_cen > table_center-1 and temp_cen < table_center+2 and flag > 0 and dis_table < 80 then
	--	dbg.console();
			mCurrSeg = mGraph.cont
			temp_f2=currFrame
	--	dbg.console();
			objflag=1
	--	print(mDelta)
		end
	--	print(dis_table)
		local prevMotion=mMotion
		local nextSeg=mGraph[mCurrSeg.next].mot
		local nextSeg_delta=mGraph[mCurrSeg.next].dmot
		mMotion=MotionDOF(mLoader.dofInfo)

		local prevLen=prevMotion:length()
		local newLen=prevLen+nextSeg:length()
		local newActualLength=lookAhead+preFrameSet+nextSeg:length()
	--	print(prevLen)
	--	print(newLen)
	--	print(newActualLength)
	--	dbg.console();
			mDelta=mDelta+newLen-newActualLength
		--	print(mDelta)
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
	
		--print(temp_cen);
		--walking
		if temp_cen < table_center-1 and flag > 0 then
			turn(-6)
		elseif temp_cen > table_center+2.5 and flag > 0 then
			turn(1)
		end
		
		if flag == 11 then
			flag = 0
		end

		flag = flag +1 
	end

	if true then

		local currFrame=math.round(mTime*100)-mDelta -- 프레임단위
--	print(currFrame);
	--	print(mMotion:length());
		local curPos=mMotion:row(currFrame):toVector3(0) -- meter to cm
		local curOri=mMotion:row(currFrame):toQuater(3):rotationY()
		local curFrontDir=rotate(vector3(0,0,1), curOri) -- z axis is the local front (usually)
		local obj_pos = g_motions2[2]:row(0):toVector3(0)
--		dbg.draw('Line', curPos, curPos+curFrontDir*100, "front direction", "solidblue")
		dis_table=curPos.z-obj_pos.z	
		temp_cen=(curPos+curFrontDir*100).x
	end
--	print(currFrame-mDelta)
--	print(mMotion:numFrames())
	mSkin:setPoseDOF(mMotion:row(currFrame-mDelta))
	print(currFrame)
	if currFrame > 430 then
		i= i+1
		if i==1 then
			temp_f1=	currFrame
--		dbg.console();
	end
	end

	if objflag == 1 then
		temp_f3 = temp_f2 - temp_f1
	--	dbg.console();
		g_skins[1]:setPoseDOF(g_motions2[1]:row(currFrame-temp_f3))
	end
end
end

function onCallback(w, userData)
	if w:id()=="lturn" then
	   turn(5)
    elseif w:id()=="rturn" then
	   turn(-5)
    elseif w:id()=="sliderx" or w:id()=="slidery" or w:id()=="sliderz" then
	   local xx = this:findWidget('sliderx'):sliderValue()
	   local yy = this:findWidget('slidery'):sliderValue()
	   local zz = this:findWidget('sliderz'):sliderValue()
       local  m= 2
	   for m=1,2 do
		   for i=0,1952 do
		   g_motions2[m]:row(i):setVec3(0, g_motions2[m]:row(i):toVector3()+vector3(xx,yy,zz))
	   end
	   g_skins[m]:setPoseDOF(g_motions2[m]:row(0))
	   end
	   table_center = g_motions2[2]:row(0)(0)
	elseif w:id() == "turn" then
		sec_start =1
	end
    print('oncallback')
end

function dtor()
	dbg.finalize()
end

if EventReceiver then
	--class 'EVR'(EventReceiver)
	EVR=LUAclass(EventReceiver)
	function EVR:__init(graph)
		--EventReceiver.__init(self)
		self.currFrame=0
		self.cameraInfo={}
	end
		print('dtor')
end

