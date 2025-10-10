DisplacementMapModule={}

-- extract key-frames
-- time: intvectorn
-- returns joint_angles (quaternion format)
function DisplacementMapModule.samplePoses(motdof, time)
	local poses={}
	if not time then
		time=intvectorn()
		time:colon(0, motdof:numFrames(), 1)
	end
	local numFrames=time:size()
	poses[0]=vector3N(numFrames)
	local loader=motdof.dofInfo:skeleton()
	for j=1,loader:numBone()-1 do
		poses[j]=quaterN(numFrames)
	end
	local fk=loader:fkSolver()
	for i=0, numFrames-1 do
		fk:setPoseDOF(motdof:row(time(i)))
		poses[0]:row(i):assign(fk:localFrame(1).translation)
		for j=1,loader:numBone()-1 do
			poses[j]:row(i):assign(fk:localFrame(j).rotation)
		end
	end
	--print('samplePoses2:', poses[0]:rows())
	return poses
end


-- edited: output motiondof 
-- original: input motiondof 
-- kernelSize: optional
function DisplacementMapModule.interpolateMotionDOF( edited, original, key_time, edited_joint_angles, original_joint_angles, kernelSize)
--- following functions are private functions
	local function displacement(poses1, poses2)
		local out=matrixn(poses1[0]:rows(), 3+#poses1*4)
		out:sub(0,0, 0,3):assign(poses1[0]:matView()-poses2[0]:matView())

		local tempq=quaterN(poses1[1]:rows())
		for j=1, #poses1 do
			local q1=poses1[j]
			local q2=poses2[j]
			for i=0,q1:rows()-1 do
				tempq(i):difference(q1(i), q2(i))
			end
			tempq(0):align(quater(1,0,0,0))
			tempq:align()
			out:sub(0,0, 3+(j-1)*4, 3+j*4):assign(tempq:matView())
		end
		return out
	end
	local function applyDisplacement(output_poses, input_poses, disp)
		local out=output_poses:matView():sub(0, disp:rows(),0,0)
		local input=input_poses:matView():sub(0, disp:rows(),0,0)

		out:sub(0,0,0,3):assign(input:sub(0,0,0,3)- disp:sub(0,0,0,3))

		local mLoader=output_poses.dofInfo:skeleton()
		local fk=mLoader:fkSolver()
		--local conpos=vector3N(2)
		--local conori=quaterN(2)

		for i=0, input:rows()-1 do
			fk:setPoseDOF(input:row(i))
			--for c=0, 1 do
			--	local tf=fk:globalFrame(mEffectors_foot(c).bone:treeIndex())
			--	conpos(c):assign(tf.translation)
			--	conori(c):assign(tf.rotation)
			--end

			fk:localFrame(1).translation:assign(out:row(i):toVector3(0))
			for j=1,mLoader:numBone()-1 do
				local q=disp:row(i):toQuater(3+(j-1)*4)
				q:normalize()
				fk:localFrame(j).rotation:leftMult(q)
			end
			fk:forwardKinematics()
			fk:getPoseDOFfromGlobal(out:row(i))
			--local pose=out:row(i)
			--mIK_foot:IKsolve3(pose, MotionDOF.rootTransformation(pose), conpos, conori, CT.vec(1,1))
		end
		--[[
		local out=matrixn(poses1[0]:rows(), 3+#poses1*4)
		out:sub(0,0, 0,3):assign(poses1[0]:matView()-poses2[0]:matView())

		local tempq=quaterN(poses1[1]:rows())
		for j=1, #poses1 do
		local q1=poses1[j]
		local q2=poses2[j]
		for i=0,q1:rows()-1 do
		tempq(i):difference(q1(i), q2(i))
		end
		tempq(0):align(quater(1,0,0,0))
		tempq:align()
		out:sub(0,0, 3+(j-1)*4, 3+j*4):assign(tempq:matView())
		end
		return out
		]]--
	end
	local disp=displacement(original_joint_angles, edited_joint_angles)

	if kernelSize then
		math.filter(disp, kernelSize)
	end

	if dbg.lunaType(key_time)=='intvectorn' then
		key_time=key_time:toVectorn()
	end
	local sp=math.NonuniformSpline(key_time, disp)

	local numFrames=key_time(key_time:size()-1)+1
	local time2=vectorn(numFrames)
	time2:colon(0, 1, numFrames)
	local points=matrixn()
	sp:getCurve(time2, points)
	applyDisplacement(edited, original, points)
end

