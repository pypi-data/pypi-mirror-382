
FootRetargetPerFrame=LUAclass() 
FootRetargetPerFrame_State=LUAclass() 

function FootRetargetPerFrame:__init(loader, mot, toe_localpos)
	self.loader=loader
	self.mot=mot
	require('moduleIK')
	local ik_config={
		{ bone=loader:getBoneByVoca(MotionLoader.LEFTANKLE), lpos=toe_localpos, reversed=false, },
		{ bone=loader:getBoneByVoca(MotionLoader.RIGHTANKLE), lpos=toe_localpos, reversed=false, }
	}

	self.solver=createLimbIksolverToeOnly(loader, ik_config)
	self.CONTINUED_CON=0
	self.STARTED_CON=1
	self.ENDED_CON=2
	self.NO_CON=3
	self.lastEdited=-1

	self.states={ 
		FootRetargetPerFrame_State(), -- L
		FootRetargetPerFrame_State(), -- R
	}

end

	
function FootRetargetPerFrame:getFootPrint(mot,iframe, constraint, ieff )
	local fp={}
	local pose=mot:pose(iframe)

	local eff=self.solver.effectors
	if(pose:getConstraint(constraint)) then
		if iframe~=0 and mot:pose(iframe-1):getConstraint(constraint) then
			self.loader:setPose(mot:pose(iframe-1))
			fp.conPos=eff:getCurrentPosition(ieff)
			fp.constraint=self.CONTINUED_CON
		else 
			self.loader:setPose(mot:pose(iframe))
			fp.conPos=eff:getCurrentPosition(ieff)
			fp.constraint=self.STARTED_CON;
			fp.start=iframe;
		end
	elseif(iframe~=0 and mot:pose(iframe-1):getConstraint(constraint)) then
		fp.constraint=self.ENDED_CON;
	else
		fp.constraint=self.NO_CON;
	end
	return fp
end
function FootRetargetPerFrame_State:__init()
	self.delta=vector3(0,0,0)
end
function FootRetargetPerFrame_State:edit(foot, m_mot, conPos, con, ieff, iframe)
	local footprint=foot:getFootPrint(m_mot, iframe, con, ieff);

	if footprint.constraint==foot.STARTED_CON or footprint.constraint==foot.CONTINUED_CON then 
		if footprint.constraint~=foot.STARTED_CON and self.prevConPos~=nil then
			self.delta=self.prevConPos-conPos(ieff)
			conPos(ieff):assign(self.prevConPos)
		else
			self.delta=vector3(0,0,0)
		end
	else
		conPos(ieff):radd(self.delta)
		self.delta:scale(0.5)
	end
	self.prevConPos=conPos(ieff):copy()
end
-- startSafe부터 nextPlayEnd까지는 정확히 constriant를 만족시킨다. startSafe앞쪽으로는 건드리지 않고,
-- nextPlayEnd이후로는 error를 propagate하는데 쓸수 있다.
function FootRetargetPerFrame:edit(mHuman, iframe)
	if iframe <= self.lastEdited then 
		return 
	elseif iframe>self.lastEdited+5 then
		self.lastEdited=iframe -- restart
		return 
	end
	local startSafe=self.lastEdited+1

	local conPos
	local pose, dof
	local loader=self.loader
	for i=startSafe, iframe do
		pose=mHuman:pose(i)
		dof=pose:toDOF(loader)

		loader:setPoseDOF(dof)
		conPos=self.solver.effectors:getCurrentPosition()
		self.states[1]:edit(self, self.mot, conPos, Motion.CONSTRAINT_LEFT_TOE, 0, i);
		self.states[2]:edit(self, self.mot, conPos, Motion.CONSTRAINT_RIGHT_TOE, 1, i);
	end

	local legLen=self.solver:IKsolve(dof, conPos)
	self.lastEdited=iframe
	return pose, dof, legLen
end
