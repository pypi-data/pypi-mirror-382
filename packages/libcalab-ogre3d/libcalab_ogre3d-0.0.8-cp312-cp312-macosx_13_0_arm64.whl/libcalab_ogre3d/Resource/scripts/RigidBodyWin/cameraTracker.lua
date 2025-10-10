
if EventReceiver then
	--class 'EVR'(EventReceiver)
	EVR=LUAclass(EventReceiver)
	function EVR:__init(graph)
		--EventReceiver.__init(self)
		self.currFrame=0
		self.cameraInfo={}
	end
end
function EVR:detachCamera()
	self.trajectory=nil
	self.trajectoryOri=nil
end

function EVR:attachCamera(filtersize)

	filtersize=filtersize or 63
	if mMotionDOFcontainer~=nill then

		local discont=mMotionDOFcontainer.discontinuity
		local mMotionDOF=mMotionDOFcontainer.mot

		self.trajectory=matrixn(mMotionDOFcontainer:numFrames(),3)

		self.trajectoryOri=matrixn(mMotionDOFcontainer:numFrames(),4)
		local segFinder=SegmentFinder(discont)

		for i=0, segFinder:numSegment()-1 do
			local s=segFinder:startFrame(i)
			local e=segFinder:endFrame(i)

			for f=s,e-1 do
				self.trajectory:row(f):setVec3(0, MotionDOF.rootTransformation(mMotionDOF:row(f)).translation)
				--self.trajectory:row(f):set(1,0)
				self.trajectoryOri:row(f):setQuater(0, MotionDOF.rootTransformation(mMotionDOF:row(f)).rotation:rotationY())
			end
			print("filtering",s,e)
			if e-s>filtersize+1 then
				math.filter(self.trajectory:range(s,e,0, 3), filtersize)
				math.filter(self.trajectoryOri:range(s,e,0, 4), filtersize)
			end
		end

		local curPos=self.trajectory:row(self.currFrame):toVector3(0)*100
		self.cameraInfo.vpos=RE.viewpoint().vpos-curPos
		self.cameraInfo.vat=RE.viewpoint().vat-curPos
		self.cameraInfo.dist=RE.viewpoint().vpos:distance(curPos)
		self.cameraInfo.refRot=self.trajectoryOri:row(self.currFrame):toQuater(0):rotationY()
	end
end

function EVR:onFrameChanged_cameraOnly(win, iframe)

	self.currFrame=iframe
	if self.trajectory then
		if self.currFrame<self.trajectory:rows() then
			local mMotionDOF=mMotionDOFcontainer.mot
			local curPos=self.trajectory:row(self.currFrame):toVector3(0)*100
			local pPos=
				MotionDOF.rootTransformation(mMotionDOF:row(self.currFrame)).translation
			local currRot=
			self.trajectoryOri:row(self.currFrame):toQuater(0):rotationY()
			
			if debugVis then
				dbg.draw('Line', pPos*100, pPos*100+rotate(vector3(0,0,100), currRot), 'prot')
			end

			if self.cameraInfo.attachToBody then
				local tf=transf()
				tf:identity()
				tf:leftMultTranslation(curPos*-1)
				local qd=quater()
				qd:difference(self.cameraInfo.refRot, currRot)
				tf:leftMultRotation(qd)
				tf:leftMultTranslation(curPos)

				RE.viewpoint().vpos:assign(tf*(self.cameraInfo.vpos+curPos))
				RE.viewpoint().vat:assign(tf*(self.cameraInfo.vat+curPos))
				RE.viewpoint():update()     
			else
				RE.viewpoint().vpos:assign(self.cameraInfo.vpos+curPos)
				RE.viewpoint().vat:assign(self.cameraInfo.vat+curPos)
				RE.viewpoint():update()     
			end
		end
	end
end

-- override this function
function EVR:onFrameChanged(win, iframe)
	self:onFrameChanged_cameraOnly(win, iframe)
end
