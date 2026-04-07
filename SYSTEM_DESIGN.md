# System design Q&A

This document describe typical questions related to how the system should handle different types of scenarios.

Q: The size of the URL list could grow infinitely. How might you scale this beyond the memory capacity of the system?

- A: A: If the list grows exponentially, it will have a huge impact on the application's RAM usage, eventually causing the server to crash. To handle this, it is much better to move the data out of application memory and use a dedicated Database to query it efficiently. By this, I mean using proper indexing on the database tables so we don't perform slow full-table scans. We can also take advantage of Redis cache system, to query the most common ones.

Q: Assume that the number of requests will exceed the capacity of a single system, describe how might you solve this, and how might this change if you have to distribute this workload to an additional region, such as Europe. 

- A: I would scale horizontally, placing multiple instances of the application behind an Application Load Balancer (ALB) and use an Auto Scaling Group to automatically spin up new containers/VMs when traffic spikes. 
- If we need to distribute this to an additional region like Europe, the architecture changes. I would deploy a replica of the application and the database in the EU region. Then, I would use DNS Latency-Based Routing (like AWS Route 53) to direct users to the region closest to them. 

Q: What are some strategies you might use to update the service with new URLs? Updates may be as much as 5 thousand URLs a day with updates arriving every 10 minutes.

- A: I would develop a small background task to sync and update the database, completely decoupled from the main app. It is not a good practice to use the main API's resources for background syncing. I would program the task to process updates efficiently without overwhelming the database with multiple connections or heavy I/O processes. 
- It is worth mentioning that using a Serverless function (like AWS Lambda) could be a solution here, but I prefer a dedicated worker depending on whether the database is exclusive to this application or shared, to avoid timeout issues with large syncs.

Q: You’re woken up at 3am, what are some of the things you’ll look for in the app?
- A: I would look at logs, Grafana panels (or any monitoring dashboard), and check metrics to validate if something unusual happened (like high error rates or latency spikes). If proper monitoring wasn't implemented yet, I would SSH into the deployment server (EC2 or VM) and use commands like docker logs <container_id> and docker stats to see what is failing.

Q: Does that change anything you’ve done in the app?
- A: Yes, observability is a critical part of any application. If the sync service fails for any reason, we will have an outdated database, meaning the proxy server cannot rely entirely on this application. 
- To solve this, the app itself needs to expose metrics (like a /metrics endpoint). I would set up a Grafana panel to check Prometheus metrics like RAM usage, CPU, and network I/O. I would also add Promtail and Loki to aggregate and retain logs outside the app itself, so if we need to know what happened 3 days ago, we can just query it without touching the server.

Q: What are some considerations for the lifecycle of the app?
- A: We are missing a very important part here, which is CI/CD. If we relied on manual updates, I would have to build the container, push it to a registry, SSH to a VM, pull the image, and deploy it. This works for a prototype, but it is way too hard to debug, maintain, and makes the workflow slow. 
- The best idea is to use a CI tool. Every time I push changes to the main branch (or dev, stage, etc.), a CI pipeline should run the automated tests and build the application. If it passes, it tags a specific version and pushes it to the container registry. Finally, a CD Agent should be actively listening to the registry so when a new version is released, it deploys the new image automatically to the environment.

Q: You need to deploy a new version of this application. What would you do?
- A: I would create a new release on the source control tool (GitHub, GitLab, etc.), briefly describe the new features or enhancements, and then wait for the CI/CD pipeline to tag and deploy it automatically. Because this service blocks users from accessing websites while it checks URLs, it cannot go down. Therefore, the deployment must be a rolling update or a Blue/Green deployment to ensure zero downtime during the switch.
  
**Sources used to answer and implement the application**: 

- https://fastapi.tiangolo.com/tutorial/path-params/?h=path
- https://docs.aws.amazon.com/whitepapers/latest/real-time-communication-on-aws/cross-region-dns-based-load-balancing-and-failover.html
- https://docs.aws.amazon.com/lambda/latest/dg/configuration-timeout.html
- https://medium.com/@sofiasondh/what-is-index-in-sql-142c50983328
- Gemini Pro 3.1 & ChatGpt (Regex)
