Herein (this folder) lies code that is written for delivery to CHTC.

Importantly, `python.tar.gz` is nicely packed with all appropriate modules
installed.

Simply put the three files (`python.tar.gz`, `run_python.sh`, and
`submit_gencat.sub`) into some working directory on your CHTC server (e.g.,
through sftp), and then enter:
```bash
user@submit$ condor_submit submit_gencat.sub
```

To check status of jobs, enter:
```bash
user@submit$ condor_q
```

To remove jobs,
```bash
user@submit$ condor_rm <ID>
```
where `<ID>` is the number assigned to your job when you submitted
it. It can be found by running `condor_q`.
