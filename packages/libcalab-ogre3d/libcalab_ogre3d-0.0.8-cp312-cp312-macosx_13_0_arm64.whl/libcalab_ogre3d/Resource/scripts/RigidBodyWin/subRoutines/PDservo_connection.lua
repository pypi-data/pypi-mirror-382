function Physics.DynamicsSimulator:getConnectionState(ichara,  q,  dq)

	local iboneAll=intvectorn()
	local localposAll=vector3N()
	local skel=self:skeleton(ichara)
	skel:_getAllRelativeConstraints(iboneAll, localposAll)

	local numCon=iboneAll:size()/2

	q:setSize(numCon)
	dq:setSize(numCon)

	local ws=self:getWorldState(ichara)

	for i=0, numCon-1 do
		local parent_bone=iboneAll(i*2)
		local child_bone=iboneAll(i*2+1)


		local parent_global=ws:globalFrame(parent_bone).rotation
		local child_global=ws:globalFrame(child_bone).rotation

		local invR1=parent_global:inverse()

		q(i):assign(invR1*child_global)

		local parent_loc_ang_vel=invR1*self:getWorldAngVel(ichara, skel:VRMLbone(parent_bone))
		local child_loc_ang_vel=child_global:inverse()*self:getWorldAngVel(ichara, skel:VRMLbone(child_bone))


		local t_rel_att=q(i):inverse()

		local rel_ang_vel=dq(i)
		rel_ang_vel:rotate(t_rel_att, parent_loc_ang_vel);
		rel_ang_vel:scale(-1)
		rel_ang_vel:radd(child_loc_ang_vel)  -- represented in the child frame
	end
end

function Physics.DynamicsSimulator:setConnectionU(ichara,  cf)
	local iboneAll=intvectorn()
	local localposAll=vector3N()
	local skel=self:skeleton(ichara)
	skel:_getAllRelativeConstraints(iboneAll, localposAll)

	local numCon=iboneAll:size()/2
	for i=0, numCon-1 do
		local parent_ibone=iboneAll(i*2)
		local child_ibone=iboneAll(i*2+1)

		local q=self:getWorldState(ichara):globalFrame(parent_ibone).rotation
		local tau=cf(i):copy()
		tau:rotate(q)

		self:addWorldTorqueToBone(ichara, skel:VRMLbone(parent_ibone), -tau)
		self:addWorldTorqueToBone(ichara, skel:VRMLbone(child_ibone), tau)

	end
end

defineDerived(Physics.DynamicsSimulator, {
	Physics.DynamicsSimulator_TRL_LCP,
	Physics.DynamicsSimulator_TRL_softbody
}, {"setConnectionU", "getConnectionState"})

PoseMaintainer_connection=LUAclass()


function PoseMaintainer_connection:__init(skeletonIndex)
	assert(skeletonIndex)
	self.theta=quaterN()
	self.dtheta=vector3N()
	self.theta_d=quaterN() -- desired q
	self.dtheta_d=vector3N() -- desired dq
	self.controlforce=vector3N()

	self.skeletonIndex=skeletonIndex or 0
end

function PoseMaintainer_connection:init(skel, simulator, k_p, k_d)
	local si=self.skeletonIndex
	simulator:getConnectionState(si, self.theta_d, self.dtheta_d)

	local q=self.theta_d
	local dq=self.dtheta_d

	self.k_p=k_p
	self.k_d=k_d
end

function PoseMaintainer_connection:generateTorque(simulator)
	local si=self.skeletonIndex
	simulator:getConnectionState(si, self.theta, self.dtheta)

	local numBallJoints=self.theta_d:size()
	self.controlforce:setSize(numBallJoints)

	-- now consider ball joints
	for i=0, numBallJoints-1 do
		local currentQuat=self.theta(i)
		local desiredQuat=self.theta_d(i)
		local relRot=currentQuat:inverse()*desiredQuat
		local qError=relRot:rotationVector() -- rotation vector

		local qdoterr=self.dtheta_d(i)-self.dtheta(i)

		local force=self.k_p*qError+self.k_d*qdoterr

		self.controlforce(i):assign(force)
	end
end
function PoseMaintainer_connection:resetParam(kp, kd, theta_d)
	self.kp:setAllValue(kp)
	self.kd:setAllValue(kd)
	self.theta_d:assign(theta_d)
end
SoftConnectionServo=LUAclass()

function SoftConnectionServo:__init(skeletonIndex, loader, info)
	assert(skeletonIndex)

	local n=#info
	self.theta_d=vectorn(n) 
	self.dtheta_d=vectorn(n) 

	self.info={}
	for i,v in ipairs(info) do
		self.info[i]={ 
			loader:getTreeIndexByName(v[1]),
			loader:getTreeIndexByName(v[2]),
		}

		assert(self.info[i][1]~=-1)
		assert(self.info[i][2]~=-1)
	end

	self.loader=loader
	self.skeletonIndex=skeletonIndex or 0
end

function SoftConnectionServo:init(simulator, k_p, k_d)
	local si=self.skeletonIndex

	local loader=self.loader
	self.simulator=simulator
	for i,info in ipairs(self.info) do
		local p1=simulator:getWorldPosition(si, loader:VRMLbone(info[1]), vector3(0,0,0))
		local p2=simulator:getWorldPosition(si, loader:VRMLbone(info[2]), vector3(0,0,0))
		self.theta_d:set(i-1, p1:distance(p2))
	end
	self.dtheta_d:setAllValue(0)

	self.k_p=k_p
	self.k_d=k_d
end
function SoftConnectionServo:addSpringForce()
	local si=self.skeletonIndex
	local loader=self.loader
	local simulator=self.simulator

	for i,info in ipairs(self.info) do
		local b1=loader:VRMLbone(info[1])
		local b2=loader:VRMLbone(info[2])
		local p1=simulator:getWorldPosition(si, b1, vector3(0,0,0))
		local p2=simulator:getWorldPosition(si, b2, vector3(0,0,0))
		local v1=simulator:getWorldVelocity(si, b1, vector3(0,0,0))
		local v2=simulator:getWorldVelocity(si, b2, vector3(0,0,0))

		local theta=p1:distance(p2)

		local dir=p2-p1
		dir:normalize()
		local dtheta=(v2-v1):dotProduct(dir)

		local u=self.k_p*(self.theta_d(i-1)-theta) + self.k_d*(self.dtheta_d(i-1)-dtheta)
		local q1=simulator:getWorldState(si):globalFrame(b1).rotation
		local q2=simulator:getWorldState(si):globalFrame(b2).rotation
		simulator:addForceToBone(si, b1, vector3(0,0,0), q1:inverse()*(-u*dir))
		simulator:addForceToBone(si, b2, vector3(0,0,0), q2:inverse()*(u*dir))
		--RE.output2("con"..si, theta, dtheta, u)
	end
end
