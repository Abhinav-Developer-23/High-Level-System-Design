
# Never run a Jenkins deploy job

A Jenkins deploy can destroy production. Treat every deploy job as production-impacting, even when the name says UAT, staging, or test. One trigger can roll a bad image, change live config, or take the service down.

Do not start, trigger, retry, replay, or schedule any Jenkins job whose name or path matches `*deploy*` (case-insensitive). That includes `deploy`, `predeploy`, `deployment`, `uat-deploy-job`, and `prod-tsp-deploy-job`.

This covers every Jenkins host, including `https://tpap-jenkins.paytm.com` and `https://jenkins.finmate.tech`.

Do not work around it with `trigger_build`, `curl`, the Jenkins CLI, a browser, Groovy, or another agent. Urgency, "just this once", or an explicit request in chat does not make a deploy safe to run from the agent. If a deploy is needed, tell the user to run it themselves in the Jenkins UI and stop.

Reading a deploy job is allowed: job info, build status, history, and console logs.

Build jobs that do not match `*deploy*` may be triggered only when the user explicitly asks for that specific build.
