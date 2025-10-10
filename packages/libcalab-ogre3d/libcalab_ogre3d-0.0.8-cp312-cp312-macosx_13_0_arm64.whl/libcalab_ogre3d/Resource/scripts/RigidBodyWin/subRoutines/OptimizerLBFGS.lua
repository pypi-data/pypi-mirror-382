local LBFGS_opta=LUAclass(OptimizeAnalytic)
local useLuaImpl=false
function LBFGS_opta:__init(ndim, thr, num_constant_var_front, num_constant_var_back)
	assert(ndim)
	if not num_constant_var_front then num_constant_var_front=0 end
	if not num_constant_var_back then num_constant_var_back=0 end

	self.num_constant_var_front=num_constant_var_front
	self.num_constant_var_back=num_constant_var_back
	local method=Optimize.LBFGS_METHOD(thr or 1e-5)
	self.method=method

	self.ndiscard=num_constant_var_front+num_constant_var_back
	self:init(0, ndim-self.ndiscard, 1, 0,method)

	if useLuaImpl then
		-- lua impl
		self.terms={}
		self.var_terms=vecIntvectorn()
		self.var_terms:resize(ndim)
		self.var_termCoeffs=vecVectorn()
		self.var_termCoeffs:resize(ndim)
	else
		-- c++ impl
		self:_initSquareTerms(ndim)
	end
	self.pos=vectorn(ndim)
	self.grad=vectorn(ndim)
end
function LBFGS_opta:_gradientFunction(_pos,_grad)
	local pos, grad
	assert( self.ndiscard+_pos:size()==self.initial:size() )
	if self.ndiscard==0 then
		pos=_pos
		grad=_grad
	else
		pos=self.pos
		grad=self.grad
		pos:slice(self.num_constant_var_front, -self.num_constant_var_back):assign(_pos)
	end

	local o=0
	if useLuaImpl then
		-- lua impl
		local terms=self.terms
		-- objective function value
		for i, term in ipairs(terms) do
			local ii=term[1]
			local w=term[2]
			local v=0
			for j=0, ii:size()-1 do
				v=v+pos(ii(j))*w(j)
			end
			v=v+w(ii:size())
			term.v=v
			o=o+v*v
		end

		-- gradient
		grad:setAllValue(0)
		for i=0, grad:size()-1 do	
			local termIndex=self.var_terms(i)
			local tc=self.var_termCoeffs(i)
			for j=0, termIndex:size()-1 do
				local ti=termIndex(j)
				grad:set(i, grad(i)+ terms[ti+1].v*2*tc(j))
			end
		end


	else
		grad:setAllValue(0.0)
		o= self:_updateSquareTermsGradient(pos, grad)
		if self.customGradientFunction then
			o=o+self:customGradientFunction(pos, grad)
		end
	end
	if self.ndiscard~=0 then
		_pos:assign(pos:slice(self.num_constant_var_front, -self.num_constant_var_back))
		_grad:assign(grad:slice(self.num_constant_var_front, -self.num_constant_var_back))
	end
	return o
end

if useLuaImpl then
	-- lua impl
	function LBFGS_opta:addSquared(index, coef)
		-- add(3,0,4,1,5,2,-1) : add objective to minimize (3x+4y+5z-1)^2
		table.insert(self.terms, {index, coef})
		local iterm=#self.terms-1
		for i=0, index:size()-1 do
			self.var_terms(index(i)):pushBack(iterm)
			self.var_termCoeffs(index(i)):pushBack(coef(i))
		end
	end
end

LBFGS_opta.add=QuadraticFunctionHardCon.add
LBFGS_opta.addSystem=QuadraticFunctionHardCon.addSystem
LBFGS_opta.addSystemSelectedRows=QuadraticFunctionHardCon.addSystemSelectedRows
LBFGS_opta.addWeighted=QuadraticFunctionHardCon.addWeighted

function LBFGS_opta:solve(x)
	self.initial=x
	if self.ndiscard~=0 then
		self.pos:assign(self.initial)
	end
	self:optimize(x)
	local final=self:getResult()
	if self.ndiscard==0 then
		return final
	else
		self.pos:slice(self.num_constant_var_front, -self.num_constant_var_back):assign(final)
		return self.pos
	end
end

return LBFGS_opta
