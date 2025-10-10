
require("config")
require("module")
require("RigidBodyWin/common")
require("RigidBodyWin/IPC_based/useCases")

model_path="../Resource/scripts/ui/RigidBodyWin/"
frame_rate=120

function calcContactForce(skel, motdofcontainer, forceAll, filterWindow)

	local mot=motdofcontainer

	local aCOG=calcCOMtrajectory(skel, mot.mot, mot.discontinuity):matView()
	aLinearMomentum=aCOG:derivative( frame_rate, mot.discontinuity)
	aAggAcceleration=aLinearMomentum:derivative( frame_rate, mot.discontinuity)

	forceAll:setSize(aAggAcceleration:rows())
	for i=0, forceAll:size()-1 do
		forceAll:set(i, (aAggAcceleration:row(i):toVector3(0)+vector3(0,9.8,0)):length())
	end
	math.gaussFilter(math.calcKernelSize(filterWindow, 1/frame_rate) ,forceAll);
end

function ctor()

	this:setUniformGuidelines(10);

	this:create("Button", "load model", "load model", 0, 10);
	this:create("Button", "load gymnist", "load gymnist", 0, 10);

	this:create("Choice", "signal", "", 0,4);

	this:menuItems( "contactForce" , "Root-Hips distance" , "Root-COM distance" , "COM height" , "Root height" , "Horizontal MSE" , "None")
	
	this:create("Choice", "menu", "", 4, 8);
	this:menuItems( "Local minimum", "Local maximum", "All", "None")

	this:create("Button", "Run", "Run", 8, 10);

	
	this:setWidgetPos(3, 9);
	this:create("Value_Slider", "filterwindow", "window size");
	this:widget(0):sliderRange(0,10);
	this:widget(0):sliderValue(1.0);

	this:setWidgetPos(9, 10);
	this:create("Button", "default", "D");

	this:setWidgetPos(0, 10);
	this:create("Button", "draw segmentation", "draw segmentation");

	this:create("Button", "toggle segmentation", "toggle segmentation");
	this:widget(0):buttonShortcut('FL_CTRL+s');

	this:create("Box", "usage", "Press above button to change segmentation manually");

	this:create("Button", "save", "save");
	this:create("Button", "load classification", "load");



	this:create("Check_Button", "draw signal","draw signal");
	this:widget(0):checkButtonValue(0);

	this:updateLayout();
	mCutState=bitvectorn()
end
function dtorSub()
	if RE.motionPanelValid() then
		if mSkin then
			RE.motionPanel():motionWin():detachSkin(mSkin)
			mSkin=nil
		end
	end

	-- remove objects that are owned by LUA
	collectgarbage()
end
function dtor()
	dtorSub()
end
function _filter(signal, kernelSize) 

	signal:filter(kernelSize)
	--Motion& src=m_motionPanel->currMotion();
	--MotionUtil::SegmentFinder seg(src);
	--for(int i=0; i<seg.numSegment(); i++)
		--signal.range(seg.startFrame(i), seg.endFrame(i)).op0(m0::useUnary(m1::filter(src.KernelSize(kernelSize))));
	--end
end

function _start(chosenFile1, chosenFile2)
	dtorSub()

	if chosenFile1 and chosenFile2 then
		mLoader=MainLib.VRMLloader(chosenFile1)
		mSkin=RE.createVRMLskin(mLoader, true)
		mSkin:setThickness(0.03)
		mSkin:scale(100,100,100)
		if mLoader~=nil and chosenFile2 ~=nil then
			mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo,chosenFile2)
			mSkin:applyMotionDOF(mMotionDOFcontainer.mot)
			RE.motionPanel():motionWin():detachSkin(mSkin)
			RE.motionPanel():motionWin():addSkin(mSkin)
		end
	end
end

function onCallback(w, userData)
	if w:id()=="load model" then
		local chosenFile1=Fltk.ChooseFile("Choose a WRL file to load", model_path, "*.wrl", false)
		local chosenFile2=Fltk.ChooseFile("Choose a DOF file to load", model_path, "*.dof", false)
		_start(chosenFile1, chosenFile2)
	elseif w:id()=="toggle segmentation" then
		local curf=RE.motionPanel():scrollPanel():currFrame();
		if curf<mCutState:size() then
			local bValue=mCutState(curf);
			mCutState:set(curf, not bValue);
			RE.motionPanel():scrollPanel():setCutState(mCutState);
			RE.motionPanel():scrollPanel():redraw();
		end
	elseif (w.mId=="draw segmentation") then
		RE.motionPanel():scrollPanel():addPanel(mCutState, CPixelRGB8 (0,250,0));
	elseif w:id()=="load gymnist" then
		_start(model_path.."gymnist.wrl", model_path.."gymnist.dof")
	elseif w:id()=="save" then
		local fn=Fltk.ChooseFile("Choose seg result", "../Resource/scripts/ui/RigidBodyWin/","*.{bit,lua}",true);
		if fn then
			if string.sub(fn,-3)=="lua" then
				util.writeFile(fn, table.tostring2(mCutState))
			else
				mCutState:save(fn);
			end
		end
	elseif w:id()=="load classification" then
		local fn=Fltk.ChooseFile("Choose seg result", "../Resource/scripts/ui/RigidBodyWin/","*.{bit,lua}", false);
		if fn then
			if string.sub(fn, -3)=="lua" then
				mCutState=table.fromstring2(util.readFile(fn))
			else
				mCutState:load(mMotionDOFcontainer:numFrames(), fn)
			end
			RE.motionPanel():scrollPanel():setCutState(mCutState);
			RE.motionPanel():scrollPanel():redraw();
		end
	elseif w:id()=="Run" then
		local signal=vectorn();
		local signalType=this:findWidget("signal"):menuText();
		if(signalType=="contactForce") then
			calcContactForce(mLoader, mMotionDOFcontainer,signal, this:findWidget("filterwindow"):sliderValue());
		end
		do
			--}
			--else if(signalType=="Root-Hips distance")
			--{
			--Motion& mot=m_motionPanel->currMotion();
			--signal.setSize(mot.numFrames());
			--
			--for(int i=0; i<signal.size(); i++)
			--signal[i]=mot.pose(i).m_aTranslations[1].length();
			--
			--}
			--else if(signalType=="Root-COM distance" || signalType=="COM height")
			--{
			--Motion& src=m_motionPanel->currMotion();
			--MotionUtil::PhysicalHuman ph(src);
			--matrixn mCOM;
			--ph.COM(mCOM);
			--
			--_filter(mCOM, findSlider("filterwindow")->value());
			--
			--signal.setSize(src.numFrames());
			--
			--if(signalType=="COM height")
			--{
			--for(int i=0; i<signal.size(); i++)
			--signal[i]=mCOM[i][1];
			--}
			--else
			--{
			--for(int i=0; i<signal.size(); i++)
			--signal[i]=src.pose(i).m_aTranslations[0].y-mCOM[i][1];
			--}
			--}
			--else if(signalType=="Root height")
			--{
			--Motion& src=m_motionPanel->currMotion();
			--signal.setSize(src.numFrames());
			--
			--for(int i=0; i<signal.size(); i++)
			--signal[i]=src.pose(i).m_aTranslations[0].y;
			--}
			--else if (signalType=="Horizontal MSE")
			--{
			--Motion& src=m_motionPanel->currMotion();
			--MotionUtil::GetSignal gs(src);
			--intvectorn ajoint;
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::LEFTANKLE));
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::RIGHTANKLE));
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::LEFTKNEE));
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::RIGHTKNEE));
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::LEFTELBOW));
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::RIGHTELBOW));
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::LEFTWRIST));
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::RIGHTWRIST));
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::LEFTSHOULDER));
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::RIGHTSHOULDER));
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::CHEST2));
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::NECK));
			--ajoint.push_back(src.skeleton().getRotJointIndexByVoca(MotionLoader::HEAD));
			--
			--hypermatrixn apos;
			--gs.jointPos(ajoint, apos, MotionUtil::LOCAL_COORD);
			--
			--for(int page=0; page<apos.page(); page++)
			--{
			--for(int i=0; i<apos.page(page).rows(); i++)
			--apos[page][i][1]=0.0;
			--}
			--
			--signal.setSize(src.numFrames());
			--
			--for(int i=0; i<signal.size(); i++)
			--{
			--signal[i]=0.0;
			--for(int page=0; page<apos.page(); page++)
			--{
			--signal[i]+=SQR(apos.page(page).row(i).length());
			--}
			--}
			--
			--_filter(signal.column().lval(), findSlider("filterwindow")->value());			
			--}
			--else if(signalType=="None")
			--{
			--Motion& src=m_motionPanel->currMotion();
			--signal.setSize(src.numFrames());
			--signal.setAllValue(0);
			--}
			--else
			--Msg::error("unknown");
			--
			--
			--
		end

		local v=this:findWidget("menu"):menuValue()
		if v==0 then
			mCutState:findLocalOptimum(signal, bitvectorn.ZC_MIN);
		elseif v==1 then
			mCutState:findLocalOptimum(signal, bitvectorn.ZC_MAX);
		elseif v==2 then
			mCutState:findLocalOptimum(signal, bitvectorn.ZC_ALL);
		elseif v==3 then
			mCutState:setSize(signal:size());
			mCutState:clearAll();
		end

		if(this:findWidget("draw signal"):checkButtonValue()) then
			signal:column():drawSignals("signal.jpg",true)
			RE.motionPanel():scrollPanel():addPanel("signal.jpg");
			RE.motionPanel():scrollPanel():addPanel(mCutState, CPixelRGB8 (0,250,0));
		end
		RE.motionPanel():scrollPanel():setCutState(mCutState);
	end
end

function frameMove(fElapsedTime)
end
--[[
	}
	else if(w.mId=="toggle segmentation")
	{
		int curf=m_motionPanel->scrollPanel()->currFrame();
		if(curf<mCutState.size())
		{
			bool bValue=mCutState[curf];
			mCutState.setValue(curf, !bValue);
			m_motionPanel->scrollPanel()->setCutState(mCutState);
			m_motionPanel->scrollPanel()->redraw();
		}
	}
	else if(w.mId=="draw segmentation")
	{
		m_motionPanel->scrollPanel()->addPanel(mCutState, CPixelRGB8 (0,250,0));
	}
	else if(w.mId=="default")
	{
		OR::LUAWrap L;
		L.setVal<TString>("motionId", m_motionPanel->currMotion().GetIdentifier());
		L.dofile("../Resource/constraint.lua");

		double filterWindow;
		filterWindow=L.getValue<double>("filteringWindowSize");
	
		findSlider("filterwindow")->value(filterWindow);
	}
	else if(w.mId=="menu")
	{

	}
}


void SegmentationWin::click(int iframe)
{
	/*
	if(m_dragOperations.userData()==Hash("Split"))
	{
		if(mActor.split(iframe))
		{
			m_motionPanel->scrollPanel()->setCutState(mActor.mCutState);
			_invalidateFeatureVectors();
		}

				
	}
	else
		selected(iframe, iframe+1);*/
}

void SegmentationWin::selected(int startframe, int endframe)
{
}

#define __super FlLayout
void SegmentationWin::show()
{
	m_motionPanel->scrollPanel()->connectSelectUI(*this);	
	__super::show();
}
void SegmentationWin::hide()
{
	m_motionPanel->scrollPanel()->disconnectSelectUI(*this);
	__super::hide();
}


void SegmentationWin::panelSelected(const char* label, int iframe)
{
	/*
	mActor.mCurrClassifier=-1;
	m_output->value("none");

	for(int i=0; i<mActor.numSVM(); i++)
	{
		bool bTrainingSet;
		if((bTrainingSet=(mActor.mSVMs[i]->mName+" training set"==label))||
			mActor.mSVMs[i]->mName+" results"==label )
		{
			mActor.mCurrClassifier=i;
			_updateMenuGroup();
			int curGroup=m_menuGroup.size()-2;
	
			intvectorn isegments;
			mActor._findSegments(iframe, iframe+1, isegments);
			if(isegments.size() )
			{
				int iseg=isegments[0];
				if(bTrainingSet)
				{
					int itrn;
					itrn=mActor.mSVMs[mActor.mCurrClassifier]->findTrainingDataBySegment(iseg);
					if(itrn!=-1)
						curGroup=mActor.mSVMs[mActor.mCurrClassifier]->mTrainingData[itrn][1];
				}
				else if(mActor.mSVMs[mActor.mCurrClassifier]->mResults.size())
					curGroup=mActor.mSVMs[mActor.mCurrClassifier]->mResults[iseg];
			}
			
			m_output->value(mActor.mSVMs[mActor.mCurrClassifier]->mName);
			m_menuClassifyMethod.value(mActor.mSVMs[mActor.mCurrClassifier]->eClassifyMethod);
			m_menuGroup.value(curGroup+1);
			m_menuGroupSearch.value(curGroup+1);
			redraw();
			break;
		}
	}*/
}
FlLayout* createSegmentationWin (int x, int y, int w, int h, MotionPanel& mp,FltkRenderer& renderer)
{
	return new SegmentationWin(x,y,w,h,&mp);
}
]]--
