package.__taesooLibPath=RE.taesooLibPath()
print('\n----- relative mode ------')
print(package.__taesooLibPath)
print('--------------------------')
package.resourcePath=package.__taesooLibPath.."Resource/motion/"
package.scriptPath=package.__taesooLibPath.."Resource/scripts/"

package.path=package.path..";./?.lua" --;"..package.path
package.path=package.path..";".."work/taesooLib/Resource/scripts/?.lua"
package.path=package.path..";".."work/taesooLib/Resource/scripts/RigidBodyWin/?.lua"
package.path=package.path..";".."work/taesooLib/Resource/scripts/modules/?.lua"
package.path=package.path..";"..package.scriptPath.."?.lua"
package.path=package.path..";"..package.__taesooLibPath.."Resource/scripts/relative_mode/?.lua"
package.path=package.path..";"..package.scriptPath.."RigidBodyWin/?.lua"

require('mylib')
require('module')

