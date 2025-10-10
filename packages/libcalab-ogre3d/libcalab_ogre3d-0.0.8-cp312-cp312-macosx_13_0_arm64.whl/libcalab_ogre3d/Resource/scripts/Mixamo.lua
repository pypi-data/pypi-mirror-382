local Mixamo={ 
	footIKconfig={
		{'LeftLeg', 'LeftFoot', vector3(0.000000,-0.093740,-0.04), childCon=2 },
		{'LeftToeBase', vector3(0,0.01,0),},
		{'RightLeg', 'RightFoot', vector3(0.000000,-0.094795,-0.04), childCon=4},
		{'RightToeBase', vector3(0,0.01,0),},
	},
	voca={
		left_hip='LeftUpLeg',
		right_hip='RightUpLeg',
		left_knee='LeftLeg',
		right_knee='RightLeg',
		left_ankle='LeftFoot',
		right_ankle='RightFoot',
		left_toes='LeftToeBase',
		right_toes='RightToeBase',
		left_shoulder='LeftArm',
		right_shoulder='RightArm',
		head='Head',
	},


}

Mixamo.lafan={
	retargetConfig={
		A={
			boneCorrespondences ={
				Head ="Head",
				Hips ="Hips",
				LeftArm ="LeftArm",
				LeftFoot ="LeftFoot",
				LeftForeArm ="LeftForeArm",
				LeftHand ="LeftHand",
				LeftLeg ="LeftLeg",
				LeftShoulder ="LeftShoulder",
				LeftToe ="LeftToeBase",
				LeftUpLeg ="LeftUpLeg",
				Neck ="Neck",
				RightArm ="RightArm",
				RightFoot ="RightFoot",
				RightForeArm ="RightForeArm",
				RightHand ="RightHand",
				RightLeg ="RightLeg",
				RightShoulder ="RightShoulder",
				RightToe ="RightToeBase",
				RightUpLeg ="RightUpLeg",
				Spine1 ="Spine",
				Spine2 ="Spine1",
			},
			reusePreviousBinding =true,
			skel ="/Users/taesookwon/sample_SAMP/lafan1/aiming1_subject1.bvh",
			skinScale =0.94,
		},
		B={
			EE ={
			},
			motion ="",
			skel ="/Users/taesookwon/taesooLib/Resource/motion/Mixamo/passive_marker_man_T_nofingers.fbx.dat",
			skinScale =100,
		},
		bindposes_quat={{"__userdata", "Pose", {"__userdata", "matrixn", {{0, 91.882057189941, 0, }, }, }, {"__userdata", "matrixn", {{0.52119910967873, 0.46017326620957, 0.52772279121599, 0.48795564221281, }, {0.012858730592775, 0.053615630075146, -0.99830695602399, -0.018526705408766, }, {0.99460617274978, -0.07423455017246, -0.0069521643279197, -0.072107281878381, }, {0.80558105246345, -0.059453755195192, 0.0052697119039604, 0.58947149977036, }, {0.98252429453143, -5.0326236432175e-06, 2.6518197066786e-05, 0.18613438673972, }, {0.06584651601154, -0.069823457655907, 0.99292129325943, -0.069973041109717, }, {0.99178644312071, 0.089316696449715, 0.019140137998092, -0.089531190624814, }, {0.77591089995246, 0.07319217396565, -0.0037483537136183, 0.62657093042175, }, {0.98252428523247, 4.8985016190349e-06, -2.6747888170185e-05, 0.18613443579568, }, {0.99815987065668, 0.00095373135580639, -0.0036619901934932, 0.060519028701419, }, {0.99940249907397, 0.001643296274537, -0.0074265897010878, 0.033716319304842, }, {0.99949229347352, 0.001644196664769, -0.007420242334087, 0.030941750242496, }, {0.99739744453066, -0.023430001761392, -0.053119708386207, 0.042751248427781, }, {0.98099626137272, -0.052442597897504, 0.10008206180074, -0.15773297056804, }, {0.011111163153514, -0.70476449753853, 0.036754155043061, -0.7084014943164, }, {0.98864258207914, -0.088604542488528, 0.12131958137437, -0.0040791084110475, }, {0.97010412615921, -0.017965641117238, -0.13774142586436, -0.1990038184281, }, {0.96052618953813, 0.26741063980865, -0.0060305459148209, 0.076450123900832, }, {0.033784653401828, 0.69676659737746, -0.062631317982708, -0.71375921989233, }, {0.99192541777146, 0.053363918300428, -0.10736488816832, -0.041340519967136, }, {0.97198180944749, 0.016545145905086, 0.13793357147602, -0.18960999475245, }, {0.98966030269221, -0.12622055416549, 0.021448277757192, 0.06465932541067, }, }, }, }, {"__userdata", "Pose", {"__userdata", "matrixn", {{0, 0.97, 0, }, }, }, {"__userdata", "matrixn", {{0.98687051193922, -0.15617748288503, -0.039984859965597, 0.0098182217352106, }, {0.98866019060931, 0.14821070693914, 0.020765226470517, -0.012386251353013, }, {0.99803197613306, -0.0330475584414, -0.052410877333612, 0.0096505665174385, }, {0.99529943168399, 0.063666786275699, 0.071719524636206, -0.013486712008726, }, {0.98487979445875, -0.17170498712331, -0.015367248085285, 0.01711828116803, }, {0.99062571112767, 0.12472147837359, -0.0021823276260009, 0.055682050350526, }, {0.99839263952772, -0.055753865038738, -0.010167803527824, 0.00050955031453573, }, {0.99237294008797, -0.0032257128017838, 0.028089135244771, -0.11998559513238, }, {0.96976496133726, 0.031321680508917, -0.18160032173803, 0.15998810967469, }, {1, -1.8995222061946e-16, -2.1517076315147e-15, -6.3317406873153e-16, }, {0.99839263952772, -0.055753865038738, -0.010167803527824, 0.00050955031453573, }, {0.99280304632106, 0.016981516339164, -0.022517278087883, 0.11639034111967, }, {0.97141429221813, 1.3135943453486e-05, 0.19216897521424, -0.13937488176463, }, {0.99685669909469, 0.015870012047388, -0.0013241305362552, -0.077608703545232, }, {0.98665022329076, 0.15805979073558, 0.035904750359561, 0.015788867423587, }, {1, 2.5919121281952e-17, -1.0401564592283e-18, -6.8695073031051e-16, }, {0.99312846541117, -0.0099145122157098, 0.11660478861946, 0.00093643396863543, }, {1, 8.3483567281384e-16, 3.9628131505431e-15, 1.6523241108679e-16, }, {0.98300744505761, 0.17710946751767, 0.027321678308354, -0.039775939603213, }, {1, -2.6020852139652e-18, -1.3280392410775e-15, 4.2647092454717e-16, }, {0.98425116546985, -0.015158178902269, -0.17608057521391, 0.0039375012299167, }, {1, -1.4918621893401e-16, 6.9287295085402e-16, -8.5158659637874e-16, }, }, }, }, },
		bindposes_map={{['R']={['LeftFoot']=3, ['Hips']=0, ['LeftToe']=4, ['RightHand']=21, ['Spine']=9, ['Spine2']=11, ['Spine1']=10, ['RightShoulder']=18, ['RightFoot']=7, ['RightArm']=19, ['RightUpLeg']=5, ['Head']=13, ['LeftUpLeg']=1, ['RightForeArm']=20, ['LeftForeArm']=16, ['RightToe']=8, ['LeftHand']=17, ['LeftArm']=15, ['Neck']=12, ['LeftShoulder']=14, ['RightLeg']=6, ['LeftLeg']=2, }, ['T']={['Hips']=0, }, }, {['R']={['LeftFoot']=16, ['Hips']=0, ['LeftForeArm']=8, ['RightHand']=13, ['Spine']=1, ['Spine2']=3, ['Spine1']=2, ['RightShoulder']=10, ['RightFoot']=20, ['RightArm']=11, ['LeftShoulder']=6, ['Head']=5, ['LeftUpLeg']=14, ['RightForeArm']=12, ['RightToeBase']=21, ['Neck']=4, ['LeftHand']=9, ['RightLeg']=19, ['LeftToeBase']=17, ['RightUpLeg']=18, ['LeftArm']=7, ['LeftLeg']=15, }, ['T']={['Hips']=0, }, }, }
	},
	constraintMarkingConfig={
		filter_size=3,
		markers={
			-- testConstraintMarking.lua -> results go to ....fbx.con.lua or ...bvh.con.lua
			default_param ={
				thr_speed=0.3*111, -- speed limit
				thr_height=0.02*111,  -- height threshhold (the lower limit)
			},
			{
				"leftHeel", 
				bone='leftFoot', 
				lpos=vector3(0,-0.07,0)*111, -- local position
			},
			{
				"leftToe", 
				bone='LeftToe', 
				lpos=vector3(0,0,0),
			}, {
				"rightHeel", 
				bone='RightFoot',
				lpos=vector3(0,-0.07,0)*111,
			}, 
			{
				"rightToe", 
				bone='RightToe',
				lpos=vector3(0,0,0),
			}, 		
		}
	},
}
Mixamo.fromHanyang={
	retargetConfig={
		A={
			-- ['hanyang_name'] = mixamo_name
			boneCorrespondences ={
				Head ="Head",
				Hips ="Hips",
				LeftShoulder ="LeftArm",
				LeftAnkle ="LeftFoot",
				LeftElbow ="LeftForeArm",
				LeftWrist ="LeftHand",
				LeftKnee ="LeftLeg",
				LeftCollar ="LeftShoulder",
				LeftHip ="LeftUpLeg",
				RightShoulder ="RightArm",
				RightAnkle ="RightFoot",
				RightElbow ="RightForeArm",
				RightWrist ="RightHand",
				RightKnee ="RightLeg",
				RightCollar ="RightShoulder",
				RightHip ="RightUpLeg",
				Neck ="Neck",
				Chest ="Spine",
				Chest1 ="Spine2",
			},
			reusePreviousBinding =true,
			skel ="taesooLib/hanyang_lowdof_T_sh.wrl",
			skinScale =100,
		},
		B={
			EE ={
			},
			motion ="",
			skel ="/Users/taesookwon/taesooLib/Resource/motion/Mixamo/passive_marker_man_T_nofingers.fbx.dat",
			skinScale =100,
		},
		bindposes_quat={
			-- both uses T-pose  as identity pose.
			{
				"__userdata", "Pose", 
				{"__userdata", "matrixn", {{0, 0.91882057189941, 0, }, }, }, 
				{"__userdata", "matrixn", {{1, 0, 0, 0, },}, }, 
			},
			{
				"__userdata", "Pose", 
				{"__userdata", "matrixn", {{0, 0.91882057189941, 0, }, }, }, 
				{"__userdata", "matrixn", {{1, 0, 0, 0, },}, }, 
			}
		},
		bindposes_map={
			{
				['R']={['Hips']=0, }, 
				['T']={['Hips']=0, }, 
			}, 
			{
				['R']={['Hips']=0, }, 
				['T']={['Hips']=0, }, 
			}
		},
	},
}
Mixamo.fromHanyangM={
	retargetConfig={
		A={
			-- ['hanyang_name'] = mixamo_name
			boneCorrespondences ={
				Head ="Head",
				Hips ="Hips",
				LeftShoulder ="LeftArm",
				LeftAnkle ="LeftFoot",
				LeftElbow ="LeftForeArm",
				LeftWrist ="LeftHand",
				LeftKnee ="LeftLeg",
				LeftCollar ="LeftShoulder",
				LeftHip ="LeftUpLeg",
				RightShoulder ="RightArm",
				RightAnkle ="RightFoot",
				RightElbow ="RightForeArm",
				RightWrist ="RightHand",
				RightKnee ="RightLeg",
				RightCollar ="RightShoulder",
				RightHip ="RightUpLeg",
				Neck ="Neck",
				Chest ="Spine",
				Chest1 ="Spine2",
			},
			reusePreviousBinding =true,
			skel ="taesooLib/hanyang_lowdof_M.wrl",
			skinScale =100,
		},
		B={
			EE ={
			},
			motion ="",
			skel ="/Users/taesookwon/taesooLib/Resource/motion/Mixamo/passive_marker_man_T_nofingers.fbx.dat",
			skinScale =100,
		},
		bindposes_quat={
			-- both uses T-pose  as identity pose.
			-- hanyangM T-pose: 
			{"__userdata", "Pose", {"__userdata", "matrixn", {{0, 0.98183524, 0, }, }, }, {"__userdata", "matrixn", {{1, 0, 0, 0, }, {0.94548337601446, 0.31694238073442, -0.068476847746384, -0.030325472748542, }, {0.78776125046465, -0.60907100673055, -0.008585535645142, 0.091602454138977, }, {0.99251240029285, 0.11528493064622, -0.037996547285898, 0.013593469945898, }, {0.94548337601446, 0.31694238073442, 0.068476847746384, 0.030325472748542, }, {0.78776125046465, -0.60907100673055, 0.008585535645142, -0.091602454138977, }, {0.99251240029285, 0.11528493064622, 0.037996547285898, -0.013593469945898, }, {0.99880226189141, -0.048928944813855, 1.1828312541399e-18, -1.3629406247981e-18, }, {0.98113580382923, -0.19331977251273, 3.2486472789936e-18, -4.9491276061504e-18, }, {1, 6.0352834852935e-17, 3.8682197900469e-19, 1.4876358846367e-19, }, {0.99808792248231, -0.024781915575367, 0.048503144825734, -0.029219866484688, }, {0.90403103140877, 0.28904281731354, -0.068804168696146, 0.30732414545472, }, {0.77995340841279, 0.096008548398767, 0.5245507911546, 0.32756908712318, }, {0.97059618310176, -0.031040309340682, -0.18069060400177, 0.15598222389042, }, {0.99808792248231, -0.024781915575367, -0.048503144825734, 0.029219866484688, }, {0.90403103140877, 0.28904281731354, 0.068804168696146, -0.30732414545472, }, {0.77995340841279, 0.096008548398767, -0.5245507911546, -0.32756908712318, }, {0.97059618310176, -0.031040309340682, 0.18069060400177, -0.15598222389042, }, {0.99818099163139, 0.06028853909135, 2.3660620960627e-17, 3.2357399923593e-18, }, {0.99650915439286, -0.083483562521146, 4.3822719059973e-17, -1.1375183971127e-17, }, }, }, },
			{
				"__userdata", "Pose", 
				{"__userdata", "matrixn", {{0, 0.91882057189941, 0, }, }, }, 
				{"__userdata", "matrixn", {{1, 0, 0, 0, },}, }, 
			}
		},
		bindposes_map={
			{['R']={['RightKnee']=5, ['Chest2']=9, ['Neck']=18, ['Chest1']=8, ['RightAnkle']=6, ['RightShoulder']=15, ['LeftElbow']=12, ['LeftCollar']=10, ['LeftShoulder']=11, ['Head']=19, ['RightElbow']=16, ['LeftHip']=1, ['Chest']=7, ['LeftKnee']=2, ['RightHip']=4, ['RightWrist']=17, ['LeftWrist']=13, ['Hips']=0, ['RightCollar']=14, ['LeftAnkle']=3, }, ['T']={['Hips']=0, }, }, 
			{
				['R']={['Hips']=0, }, 
				['T']={['Hips']=0, }, 
			}
		},
	},
}

function Mixamo.createAngleRetargetFromHanyang(mHanyangLoader, mTargetLoader)
	-- a retargetConfig generated from correspondenceTools_GUI.lua (which can also be used for models with fingers)
	local retargetConfig=Mixamo.fromHanyang.retargetConfig
	
	local RET=require("retargetting/module/retarget_common")
	local mixamoLoader=mTargetLoader.loader or mTargetLoader
	if true then
		-- further adjust bindPoseB manually.
		local pose2=Pose.fromTable(retargetConfig.bindposes_quat[2])
		--pose2.translations(0).y=pose2.translations(0).y-0.05
		--
		pose2=RET.decodeBindPose(mixamoLoader, pose2, retargetConfig.bindposes_map[2])
		mixamoLoader:setPose(pose2)
		Mixamo.setNaturalFingers(mixamoLoader)
		-- update bindpose
		retargetConfig.bindposes_quat[2]=mixamoLoader:pose()
		retargetConfig.bindposes_map[2]=RET.generateBindPoseMap(mixamoLoader)
	end
	--RET.saveRetargetInfo2(retargetConfig) -- you can see the manual adjustment using correspondenceTools_GUI.lua

	retargetConfig.A.mot={
		loader=mHanyangLoader
	}
	retargetConfig.B.mot={
		loader=mixamoLoader
	}

	local ret=RET.AngleRetarget(retargetConfig, { heightAdjust=0.05})
	--local ret=RET.AngleRetarget(retargetConfig)
	return ret
end
function Mixamo.createAngleRetargetFromHanyangM(mHanyangLoader, mTargetLoader)
	-- a retargetConfig generated from correspondenceTools_GUI.lua (which can also be used for models with fingers)
	local retargetConfig=Mixamo.fromHanyangM.retargetConfig
	
	local RET=require("retargetting/module/retarget_common")
	local mixamoLoader=mTargetLoader.loader or mTargetLoader
	if true then
		-- further adjust bindPoseB manually.
		local pose2=Pose.fromTable(retargetConfig.bindposes_quat[2])
		--pose2.translations(0).y=pose2.translations(0).y-0.05
		--
		pose2=RET.decodeBindPose(mixamoLoader, pose2, retargetConfig.bindposes_map[2])
		mixamoLoader:setPose(pose2)
		Mixamo.setNaturalFingers(mixamoLoader)
		-- update bindpose
		retargetConfig.bindposes_quat[2]=mixamoLoader:pose()
		retargetConfig.bindposes_map[2]=RET.generateBindPoseMap(mixamoLoader)
	end
	--RET.saveRetargetInfo2(retargetConfig) -- you can see the manual adjustment using correspondenceTools_GUI.lua

	retargetConfig.A.mot={
		loader=mHanyangLoader
	}
	retargetConfig.B.mot={
		loader=mixamoLoader
	}

	local ret=RET.AngleRetarget(retargetConfig, { heightAdjust=0.05})
	--local ret=RET.AngleRetarget(retargetConfig)
	return ret
end

function Mixamo.createAngleRetargetFromLafan(mLafanLoader, mTargetLoader)
	-- a retargetConfig generated from correspondenceTools_GUI.lua (which can also be used for models with fingers)
	local retargetConfig=Mixamo.lafan.retargetConfig
	
	if true then
		-- further adjust bindPoseB manually.
		local pose2=Pose.fromTable(retargetConfig.bindposes_quat[2])
		--pose2.translations(0).y=pose2.translations(0).y-0.05
		mTargetLoader.loader:setPose(pose2)
		-- 머리 앞으로 더 보내기.
		local amt=5
		mTargetLoader.loader:getBoneByName('Neck'):getLocalFrame().rotation:leftMult(quater(math.rad(amt), vector3(1,0,0)))
		mTargetLoader.loader:getBoneByName('Head'):getLocalFrame().rotation:leftMult(quater(math.rad(-amt), vector3(1,0,0)))
		mTargetLoader.loader:getBoneByName('Head'):getLocalFrame().rotation:leftMult(quater(math.rad(-7), vector3(0,1,0)))


		-- 상체 약간 앞으로
		mTargetLoader.loader:getBoneByName('Spine'):getLocalFrame().rotation:leftMult(quater(math.rad(3), vector3(1,0,0)))
		mTargetLoader.loader:getBoneByName('Spine1'):getLocalFrame().rotation:leftMult(quater(math.rad(3), vector3(1,0,0)))

		-- 상체 고정한체로 힙 앞뒤로
		local amt=3
		local knee=4
		local ankle=11
		mTargetLoader.loader:getBoneByName('Spine'):getLocalFrame().rotation:leftMult(quater(math.rad(-amt), vector3(1,0,0)))
		mTargetLoader.loader:getBoneByName('Hips'):getLocalFrame().rotation:rightMult(quater(math.rad(amt), vector3(1,0,0)))
		mTargetLoader.loader:getBoneByName('LeftUpLeg'):getLocalFrame().rotation:leftMult(quater(math.rad(-amt+knee), vector3(1,0,0)))
		mTargetLoader.loader:getBoneByName('RightUpLeg'):getLocalFrame().rotation:leftMult(quater(math.rad(-amt+knee), vector3(1,0,0)))
		mTargetLoader.loader:getBoneByName('LeftLeg'):getLocalFrame().rotation:leftMult(quater(math.rad(-knee), vector3(1,0,0)))
		mTargetLoader.loader:getBoneByName('RightLeg'):getLocalFrame().rotation:leftMult(quater(math.rad(-knee), vector3(1,0,0)))
		mTargetLoader.loader:getBoneByName('LeftLeg'):getLocalFrame().rotation:leftMult(quater(math.rad(-knee), vector3(1,0,0)))
		mTargetLoader.loader:getBoneByName('RightLeg'):getLocalFrame().rotation:leftMult(quater(math.rad(-knee), vector3(1,0,0)))
		mTargetLoader.loader:getBoneByName('LeftFoot'):getLocalFrame().rotation:leftMult(quater(math.rad(ankle), vector3(1,0,0)))
		mTargetLoader.loader:getBoneByName('RightFoot'):getLocalFrame().rotation:leftMult(quater(math.rad(ankle), vector3(1,0,0)))
		mTargetLoader.loader:fkSolver():forwardKinematics()
		
		-- update bindpose
		retargetConfig.bindposes_quat[2]=mTargetLoader.loader:pose()
	end
	local RET=require("retargetting/module/retarget_common")

	RET.saveRetargetInfo2(retargetConfig) -- you can see the manual adjustment using correspondenceTools_GUI.lua


	retargetConfig.A.mot={
		loader=mLafanLoader
	}
	retargetConfig.B.mot={
		loader=mTargetLoader.loader
	}

	local ret=RET.AngleRetarget(retargetConfig, { heightAdjust=-0.02})
	--local ret=RET.AngleRetarget(retargetConfig)
	return ret
end

function Mixamo.adjustPassiveMarkerManT(fbxloader)
	-- additional editing (캐릭터가 너무 대두고 손이 커서 고침)
	fbxloader:scaleSubtree(fbxloader.loader:getTreeIndexByName('Neck'), 0.94)
	fbxloader:scaleSubtree(fbxloader.loader:getTreeIndexByName('LeftHand'), 0.9)
	fbxloader:scaleSubtree(fbxloader.loader:getTreeIndexByName('RightHand'), 0.9)
	-- 발목이 너무 김.
	fbxloader:scaleSubtree(fbxloader.loader:getTreeIndexByName('RightFoot'),vector3(1, 0.9, 1))
	fbxloader:scaleSubtree(fbxloader.loader:getTreeIndexByName('LeftFoot'),vector3(1, 0.9, 1))

	-- additional editing (캐릭터가 허리가 길어서 고침) 
	--fbxloader:scaleBone(fbxloader.loader:getTreeIndexByName('Hips'),vector3(1,0.9,1))
	--xloader:scaleBone(fbxloader.loader:getTreeIndexByName('Spine'),vector3(1,0.9,1))
	--fbxloader:scaleBone(fbxloader.loader:getTreeIndexByName('Spine1'),vector3(1,0,1))
	--fbxloader:scaleBone(fbxloader.loader:getTreeIndexByName('Spine2'),vector3(1,0,1))
end

-- adjust fingers (주먹쥐기) 
function Mixamo.setNaturalFingers(l)

	-- adjust fingers (주먹쥐기) 
	function adjustFinger(l, name, angle)
		local q=quater(math.rad(angle), vector3(0,0,-1))
		local b=l:getBoneByName(name)
		b:getLocalFrame().rotation:assign(q)
		b:parent():getLocalFrame().rotation:assign(q)
		b:parent():parent():getLocalFrame().rotation:assign(q)
		b:parent():parent():parent():getLocalFrame().rotation:assign(q)
	end
	function adjustThumb(l, name, angle, axis)
		local q=quater(math.rad(angle), axis)
		local b=l:getBoneByName(name)
		b:getLocalFrame().rotation:assign(q)
		b:parent():getLocalFrame().rotation:assign(q)
		--b:parent():parent():getLocalFrame().rotation:assign(q)
	end

	--'RightHandThumb3',
	local f=1
	adjustThumb(l, 'LeftHandThumb3', 30*f, quater(math.rad(-30), vector3(0,1,0))*vector3(1,0,0))
	adjustFinger(l, 'LeftHandIndex4', 60*f)
	adjustFinger(l, 'LeftHandMiddle4',60*f)
	adjustFinger(l, 'LeftHandRing4',65*f)
	adjustFinger(l, 'LeftHandPinky4',70*f)
	f=f*-1
	adjustThumb(l, 'RightHandThumb3', 30*f, quater(math.rad(30), vector3(0,1,0))*vector3(-1,0,0))
	adjustFinger(l, 'RightHandIndex4', 60*f)
	adjustFinger(l, 'RightHandMiddle4',60*f)
	adjustFinger(l, 'RightHandRing4',65*f)
	adjustFinger(l, 'RightHandPinky4',70*f)

	l:updateBone()
end
return Mixamo
