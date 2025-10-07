import sys
import ctypes
from Phidget22.PhidgetSupport import PhidgetSupport
from Phidget22.Async import *
from Phidget22.DriveMode import DriveMode
from Phidget22.PhidgetException import PhidgetException

from Phidget22.Phidget import Phidget

class BLDCMotor(Phidget):

	def __init__(self):
		Phidget.__init__(self)
		self.handle = ctypes.c_void_p()
		self._setTargetVelocity_async = None
		self._onsetTargetVelocity_async = None

		if sys.platform == 'win32':
			self._BrakingStrengthChangeFactory = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double)
		else:
			self._BrakingStrengthChangeFactory = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double)
		self._BrakingStrengthChange = None
		self._onBrakingStrengthChange = None

		if sys.platform == 'win32':
			self._PositionChangeFactory = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double)
		else:
			self._PositionChangeFactory = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double)
		self._PositionChange = None
		self._onPositionChange = None

		if sys.platform == 'win32':
			self._VelocityUpdateFactory = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double)
		else:
			self._VelocityUpdateFactory = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double)
		self._VelocityUpdate = None
		self._onVelocityUpdate = None

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_create
		__func.restype = ctypes.c_int32
		res = __func(ctypes.byref(self.handle))

		if res > 0:
			raise PhidgetException(res)

	def __del__(self):
		Phidget.__del__(self)

	def _localBrakingStrengthChangeEvent(self, handle, userPtr, brakingStrength):
		if self._BrakingStrengthChange == None:
			return
		self._BrakingStrengthChange(self, brakingStrength)

	def setOnBrakingStrengthChangeHandler(self, handler):
		self._BrakingStrengthChange = handler

		if self._onBrakingStrengthChange == None:
			fptr = self._BrakingStrengthChangeFactory(self._localBrakingStrengthChangeEvent)
			__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setOnBrakingStrengthChangeHandler
			__func.restype = ctypes.c_int32
			res = __func(self.handle, fptr, None)

			if res > 0:
				raise PhidgetException(res)

			self._onBrakingStrengthChange = fptr

	def _localPositionChangeEvent(self, handle, userPtr, position):
		if self._PositionChange == None:
			return
		self._PositionChange(self, position)

	def setOnPositionChangeHandler(self, handler):
		self._PositionChange = handler

		if self._onPositionChange == None:
			fptr = self._PositionChangeFactory(self._localPositionChangeEvent)
			__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setOnPositionChangeHandler
			__func.restype = ctypes.c_int32
			res = __func(self.handle, fptr, None)

			if res > 0:
				raise PhidgetException(res)

			self._onPositionChange = fptr

	def _localVelocityUpdateEvent(self, handle, userPtr, velocity):
		if self._VelocityUpdate == None:
			return
		self._VelocityUpdate(self, velocity)

	def setOnVelocityUpdateHandler(self, handler):
		self._VelocityUpdate = handler

		if self._onVelocityUpdate == None:
			fptr = self._VelocityUpdateFactory(self._localVelocityUpdateEvent)
			__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setOnVelocityUpdateHandler
			__func.restype = ctypes.c_int32
			res = __func(self.handle, fptr, None)

			if res > 0:
				raise PhidgetException(res)

			self._onVelocityUpdate = fptr

	def getAcceleration(self):
		_Acceleration = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getAcceleration
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_Acceleration))

		if result > 0:
			raise PhidgetException(result)

		return _Acceleration.value

	def setAcceleration(self, Acceleration):
		_Acceleration = ctypes.c_double(Acceleration)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setAcceleration
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _Acceleration)

		if result > 0:
			raise PhidgetException(result)


	def getMinAcceleration(self):
		_MinAcceleration = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMinAcceleration
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MinAcceleration))

		if result > 0:
			raise PhidgetException(result)

		return _MinAcceleration.value

	def getMaxAcceleration(self):
		_MaxAcceleration = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMaxAcceleration
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MaxAcceleration))

		if result > 0:
			raise PhidgetException(result)

		return _MaxAcceleration.value

	def getActiveCurrentLimit(self):
		_ActiveCurrentLimit = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getActiveCurrentLimit
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_ActiveCurrentLimit))

		if result > 0:
			raise PhidgetException(result)

		return _ActiveCurrentLimit.value

	def getBrakingEnabled(self):
		_BrakingEnabled = ctypes.c_int()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getBrakingEnabled
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_BrakingEnabled))

		if result > 0:
			raise PhidgetException(result)

		return bool(_BrakingEnabled.value)

	def setBrakingEnabled(self, BrakingEnabled):
		_BrakingEnabled = ctypes.c_int(BrakingEnabled)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setBrakingEnabled
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _BrakingEnabled)

		if result > 0:
			raise PhidgetException(result)


	def getBrakingStrength(self):
		_BrakingStrength = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getBrakingStrength
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_BrakingStrength))

		if result > 0:
			raise PhidgetException(result)

		return _BrakingStrength.value

	def getMinBrakingStrength(self):
		_MinBrakingStrength = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMinBrakingStrength
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MinBrakingStrength))

		if result > 0:
			raise PhidgetException(result)

		return _MinBrakingStrength.value

	def getMaxBrakingStrength(self):
		_MaxBrakingStrength = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMaxBrakingStrength
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MaxBrakingStrength))

		if result > 0:
			raise PhidgetException(result)

		return _MaxBrakingStrength.value

	def getCurrentLimit(self):
		_CurrentLimit = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getCurrentLimit
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_CurrentLimit))

		if result > 0:
			raise PhidgetException(result)

		return _CurrentLimit.value

	def setCurrentLimit(self, CurrentLimit):
		_CurrentLimit = ctypes.c_double(CurrentLimit)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setCurrentLimit
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _CurrentLimit)

		if result > 0:
			raise PhidgetException(result)


	def getMinCurrentLimit(self):
		_MinCurrentLimit = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMinCurrentLimit
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MinCurrentLimit))

		if result > 0:
			raise PhidgetException(result)

		return _MinCurrentLimit.value

	def getMaxCurrentLimit(self):
		_MaxCurrentLimit = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMaxCurrentLimit
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MaxCurrentLimit))

		if result > 0:
			raise PhidgetException(result)

		return _MaxCurrentLimit.value

	def getDataInterval(self):
		_DataInterval = ctypes.c_uint32()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getDataInterval
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_DataInterval))

		if result > 0:
			raise PhidgetException(result)

		return _DataInterval.value

	def setDataInterval(self, DataInterval):
		_DataInterval = ctypes.c_uint32(DataInterval)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setDataInterval
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _DataInterval)

		if result > 0:
			raise PhidgetException(result)


	def getMinDataInterval(self):
		_MinDataInterval = ctypes.c_uint32()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMinDataInterval
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MinDataInterval))

		if result > 0:
			raise PhidgetException(result)

		return _MinDataInterval.value

	def getMaxDataInterval(self):
		_MaxDataInterval = ctypes.c_uint32()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMaxDataInterval
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MaxDataInterval))

		if result > 0:
			raise PhidgetException(result)

		return _MaxDataInterval.value

	def getDataRate(self):
		_DataRate = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getDataRate
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_DataRate))

		if result > 0:
			raise PhidgetException(result)

		return _DataRate.value

	def setDataRate(self, DataRate):
		_DataRate = ctypes.c_double(DataRate)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setDataRate
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _DataRate)

		if result > 0:
			raise PhidgetException(result)


	def getMinDataRate(self):
		_MinDataRate = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMinDataRate
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MinDataRate))

		if result > 0:
			raise PhidgetException(result)

		return _MinDataRate.value

	def getMaxDataRate(self):
		_MaxDataRate = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMaxDataRate
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MaxDataRate))

		if result > 0:
			raise PhidgetException(result)

		return _MaxDataRate.value

	def getDriveMode(self):
		_DriveMode = ctypes.c_int()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getDriveMode
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_DriveMode))

		if result > 0:
			raise PhidgetException(result)

		return _DriveMode.value

	def setDriveMode(self, DriveMode):
		_DriveMode = ctypes.c_int(DriveMode)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setDriveMode
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _DriveMode)

		if result > 0:
			raise PhidgetException(result)


	def enableFailsafe(self, failsafeTime):
		_failsafeTime = ctypes.c_uint32(failsafeTime)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_enableFailsafe
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _failsafeTime)

		if result > 0:
			raise PhidgetException(result)


	def getFailsafeBrakingEnabled(self):
		_FailsafeBrakingEnabled = ctypes.c_int()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getFailsafeBrakingEnabled
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_FailsafeBrakingEnabled))

		if result > 0:
			raise PhidgetException(result)

		return bool(_FailsafeBrakingEnabled.value)

	def setFailsafeBrakingEnabled(self, FailsafeBrakingEnabled):
		_FailsafeBrakingEnabled = ctypes.c_int(FailsafeBrakingEnabled)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setFailsafeBrakingEnabled
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _FailsafeBrakingEnabled)

		if result > 0:
			raise PhidgetException(result)


	def getFailsafeCurrentLimit(self):
		_FailsafeCurrentLimit = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getFailsafeCurrentLimit
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_FailsafeCurrentLimit))

		if result > 0:
			raise PhidgetException(result)

		return _FailsafeCurrentLimit.value

	def setFailsafeCurrentLimit(self, FailsafeCurrentLimit):
		_FailsafeCurrentLimit = ctypes.c_double(FailsafeCurrentLimit)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setFailsafeCurrentLimit
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _FailsafeCurrentLimit)

		if result > 0:
			raise PhidgetException(result)


	def getMinFailsafeTime(self):
		_MinFailsafeTime = ctypes.c_uint32()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMinFailsafeTime
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MinFailsafeTime))

		if result > 0:
			raise PhidgetException(result)

		return _MinFailsafeTime.value

	def getMaxFailsafeTime(self):
		_MaxFailsafeTime = ctypes.c_uint32()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMaxFailsafeTime
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MaxFailsafeTime))

		if result > 0:
			raise PhidgetException(result)

		return _MaxFailsafeTime.value

	def getInductance(self):
		_Inductance = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getInductance
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_Inductance))

		if result > 0:
			raise PhidgetException(result)

		return _Inductance.value

	def setInductance(self, Inductance):
		_Inductance = ctypes.c_double(Inductance)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setInductance
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _Inductance)

		if result > 0:
			raise PhidgetException(result)


	def getMinInductance(self):
		_MinInductance = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMinInductance
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MinInductance))

		if result > 0:
			raise PhidgetException(result)

		return _MinInductance.value

	def getMaxInductance(self):
		_MaxInductance = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMaxInductance
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MaxInductance))

		if result > 0:
			raise PhidgetException(result)

		return _MaxInductance.value

	def getPosition(self):
		_Position = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getPosition
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_Position))

		if result > 0:
			raise PhidgetException(result)

		return _Position.value

	def getMinPosition(self):
		_MinPosition = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMinPosition
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MinPosition))

		if result > 0:
			raise PhidgetException(result)

		return _MinPosition.value

	def getMaxPosition(self):
		_MaxPosition = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMaxPosition
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MaxPosition))

		if result > 0:
			raise PhidgetException(result)

		return _MaxPosition.value

	def addPositionOffset(self, positionOffset):
		_positionOffset = ctypes.c_double(positionOffset)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_addPositionOffset
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _positionOffset)

		if result > 0:
			raise PhidgetException(result)


	def getRescaleFactor(self):
		_RescaleFactor = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getRescaleFactor
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_RescaleFactor))

		if result > 0:
			raise PhidgetException(result)

		return _RescaleFactor.value

	def setRescaleFactor(self, RescaleFactor):
		_RescaleFactor = ctypes.c_double(RescaleFactor)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setRescaleFactor
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _RescaleFactor)

		if result > 0:
			raise PhidgetException(result)


	def resetFailsafe(self):
		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_resetFailsafe
		__func.restype = ctypes.c_int32
		result = __func(self.handle)

		if result > 0:
			raise PhidgetException(result)


	def getStallVelocity(self):
		_StallVelocity = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getStallVelocity
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_StallVelocity))

		if result > 0:
			raise PhidgetException(result)

		return _StallVelocity.value

	def setStallVelocity(self, StallVelocity):
		_StallVelocity = ctypes.c_double(StallVelocity)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setStallVelocity
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _StallVelocity)

		if result > 0:
			raise PhidgetException(result)


	def getMinStallVelocity(self):
		_MinStallVelocity = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMinStallVelocity
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MinStallVelocity))

		if result > 0:
			raise PhidgetException(result)

		return _MinStallVelocity.value

	def getMaxStallVelocity(self):
		_MaxStallVelocity = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMaxStallVelocity
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MaxStallVelocity))

		if result > 0:
			raise PhidgetException(result)

		return _MaxStallVelocity.value

	def getSurgeCurrentLimit(self):
		_SurgeCurrentLimit = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getSurgeCurrentLimit
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_SurgeCurrentLimit))

		if result > 0:
			raise PhidgetException(result)

		return _SurgeCurrentLimit.value

	def setSurgeCurrentLimit(self, SurgeCurrentLimit):
		_SurgeCurrentLimit = ctypes.c_double(SurgeCurrentLimit)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setSurgeCurrentLimit
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _SurgeCurrentLimit)

		if result > 0:
			raise PhidgetException(result)


	def getMinSurgeCurrentLimit(self):
		_MinSurgeCurrentLimit = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMinSurgeCurrentLimit
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MinSurgeCurrentLimit))

		if result > 0:
			raise PhidgetException(result)

		return _MinSurgeCurrentLimit.value

	def getMaxSurgeCurrentLimit(self):
		_MaxSurgeCurrentLimit = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMaxSurgeCurrentLimit
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MaxSurgeCurrentLimit))

		if result > 0:
			raise PhidgetException(result)

		return _MaxSurgeCurrentLimit.value

	def getTargetBrakingStrength(self):
		_TargetBrakingStrength = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getTargetBrakingStrength
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_TargetBrakingStrength))

		if result > 0:
			raise PhidgetException(result)

		return _TargetBrakingStrength.value

	def setTargetBrakingStrength(self, TargetBrakingStrength):
		_TargetBrakingStrength = ctypes.c_double(TargetBrakingStrength)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setTargetBrakingStrength
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _TargetBrakingStrength)

		if result > 0:
			raise PhidgetException(result)


	def getTargetVelocity(self):
		_TargetVelocity = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getTargetVelocity
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_TargetVelocity))

		if result > 0:
			raise PhidgetException(result)

		return _TargetVelocity.value

	def setTargetVelocity(self, TargetVelocity):
		_TargetVelocity = ctypes.c_double(TargetVelocity)

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setTargetVelocity
		__func.restype = ctypes.c_int32
		result = __func(self.handle, _TargetVelocity)

		if result > 0:
			raise PhidgetException(result)


	def setTargetVelocity_async(self, TargetVelocity, asyncHandler):
		_TargetVelocity = ctypes.c_double(TargetVelocity)

		_ctx = ctypes.c_void_p()
		if asyncHandler != None:
			_ctx = ctypes.c_void_p(AsyncSupport.add(asyncHandler, self))
		_asyncHandler = AsyncSupport.getCallback()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_setTargetVelocity_async
		__func(self.handle, _TargetVelocity, _asyncHandler, _ctx)


	def getVelocity(self):
		_Velocity = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getVelocity
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_Velocity))

		if result > 0:
			raise PhidgetException(result)

		return _Velocity.value

	def getMinVelocity(self):
		_MinVelocity = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMinVelocity
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MinVelocity))

		if result > 0:
			raise PhidgetException(result)

		return _MinVelocity.value

	def getMaxVelocity(self):
		_MaxVelocity = ctypes.c_double()

		__func = PhidgetSupport.getDll().PhidgetBLDCMotor_getMaxVelocity
		__func.restype = ctypes.c_int32
		result = __func(self.handle, ctypes.byref(_MaxVelocity))

		if result > 0:
			raise PhidgetException(result)

		return _MaxVelocity.value
