=======================
System V IPC primitives
=======================

Mostly a work in progress to unlock all goodies UNIX provides.

Examples:

.. code:: Python

  import atexit
  import sysvipc

  sem = sysvipc.semget(sysvipc.IPC_PRIVATE, 1, 0o000)
  atexit.register(lambda: sysvipc.semctl(sem, 0, sysvipc.IPC_RMID))

  sysvipc.semop(sem, [(0, 1, sysvipc.SEM_UNDO)])

  curval = sysvipc.semctl(sem, 0, sysvipc.GETVAL)

  sysvipc.semop(sem, [(0, -1, sysvipc.SEM_UNDO)])
