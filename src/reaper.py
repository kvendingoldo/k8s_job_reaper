#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import argparse

from loguru import logger

from datetime import datetime

from kubernetes import client
from kubernetes import config
from kubernetes.client.rest import ApiException

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-mode", type=str, dest="run_mode",
                        default="incluster",
                        help="Run mode for script: incluster|local")
    parser.add_argument("--namespaces", type=str, dest="namespaces",
                        default=os.environ.get('NAMESPACES'),
                        help="Namespaces that will be monitored by job reaper script")
    args = parser.parse_args()

    if args.run_mode == "incluster":
        config.load_incluster_config()
    elif args.run_mode == "local":
        config.load_kube_config()

    v1batch = client.BatchV1Api()

    if args.namespaces == "all":
        v1 = client.CoreV1Api()
        namespaces = v1.list_namespace()
    else:
        namespaces = args.namespaces.split(';')

    for item in namespaces.items:
        try:
            namespace = item.metadata.name
            logger.info(f"Trying to find jobs for '{namespace}' namespace ...")
            api_response = v1batch.list_namespaced_job(namespace)

            logger.info(f"Found {len(api_response.items)} items for '{namespace}' namespace")

            for job in api_response.items:
                status = job.status

                job_name = job.metadata.name

                if status.failed:
                    logger.info(f"Failed job {job_name} has deleted for '{namespace}' namespace")

                    v1batch.delete_namespaced_job(
                        name=job_name,
                        namespace=namespace,
                        body=client.V1DeleteOptions(
                            propagation_policy='Foreground',
                        )
                    )

                if status.succeeded:
                    logger.info(f"Succeeded job {job_name} has deleted for '{namespace}' namespace")

                    now = datetime.now()
                    completion_time = status.completion_time
                    seconds_diff = (now - completion_time.replace(tzinfo=None)).total_seconds()

                    if seconds_diff >= 300:
                        v1batch.delete_namespaced_job(
                            name=job_name,
                            namespace=namespace,
                            body=client.V1DeleteOptions(
                                propagation_policy='Foreground',
                            )
                        )
        except ApiException as e:
            logger.error(f"Exception when calling BatchV1Api->list_namespaced_job: {e}")
