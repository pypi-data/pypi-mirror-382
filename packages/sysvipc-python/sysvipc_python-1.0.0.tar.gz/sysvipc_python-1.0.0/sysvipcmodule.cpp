#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <sys/sem.h>

namespace py = pybind11;

PYBIND11_MODULE(sysvipc, m) {
  m.def(
      "semget",
      [](int key, int nsems, int semflg) {
        int result = semget(key, nsems, semflg);
        if (result == -1) {
          py::set_error(PyExc_OSError, strerror(errno));
          throw pybind11::error_already_set();
        }
        return result;
      },
      "Get a System V semaphore set identifier", py::arg("key"),
      py::arg("nsems"), py::arg("semflg"));

  m.def(
      "semop",
      [](int semid, const std::vector<std::tuple<short, short, short>> &sops) {
        std::vector<sembuf> csemops(sops.size());
        for (unsigned i = 0, max = sops.size(); i < max; ++i) {
          csemops[i].sem_num = std::get<0>(sops[i]);
          csemops[i].sem_op = std::get<1>(sops[i]);
          csemops[i].sem_flg = std::get<2>(sops[i]);
        }
        py::gil_scoped_release release;
        int result = semop(semid, &csemops[0], csemops.size());
        if (result == -1) {
          py::set_error(PyExc_OSError, strerror(errno));
          throw pybind11::error_already_set();
        }
        return result;
      },
      "System V semaphore operations", py::arg("semid"), py::arg("sops"));

  m.def(
      "semctl",
      [](int semid, int semnum, int op) {
        int result = semctl(semid, semnum, op);
        if (result == -1) {
          py::set_error(PyExc_OSError, strerror(errno));
          throw pybind11::error_already_set();
        }
        return result;
      },
      "System V semaphore control operations", py::arg("semid"),
      py::arg("semnum"), py::arg("op"));

  m.attr("IPC_PRIVATE") = py::int_(IPC_PRIVATE);
  m.attr("IPC_RMID") = py::int_(IPC_RMID);
  m.attr("IPC_NOWAIT") = py::int_(IPC_NOWAIT);
  m.attr("GETVAL") = py::int_(GETVAL);
  m.attr("SEM_UNDO") = py::int_(SEM_UNDO);

  m.doc() =
      R"(Different constants:

semget() flags:
- IPC_PRIVATE - or "new", create a new semaphore.

semop() flags:
- SEM_UNDO - if an operation specifies SEM_UNDO, it will be automatically undone when the process terminates.
- IPC_NOWAIT - if IPC_NOWAIT is specified in sem_flg semop() fails with errno set to EAGAIN.

semctl() flags:
- IPC_RMID - Immediately remove the semaphore set, awakening all processes blocked in semop() calls.
- GETVAL - Return semval (i.e., the semaphore value) for the semnum-th semaphore of the set.  The calling process must have read permission on the semaphore set.
)";
}
