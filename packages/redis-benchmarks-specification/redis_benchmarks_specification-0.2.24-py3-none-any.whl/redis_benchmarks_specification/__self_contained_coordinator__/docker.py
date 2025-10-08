import logging

import docker

from redis_benchmarks_specification.__self_contained_coordinator__.cpuset import (
    generate_cpuset_cpus,
)


def generate_standalone_redis_server_args(
    binary,
    port,
    dbdir,
    configuration_parameters=None,
    redis_arguments="",
    password=None,
):
    added_params = ["port", "protected-mode", "dir", "requirepass", "logfile"]
    # start redis-server
    command = [
        binary,
        "--protected-mode",
        "no",
        "--port",
        "{}".format(port),
    ]

    # Add password authentication if provided
    if password is not None and password != "":
        command.extend(["--requirepass", password])
        logging.info("Redis server will be started with password authentication")
    if dbdir != "":
        command.extend(["--dir", dbdir])
        command.extend(["--logfile", f"{dbdir}redis.log"])
    if configuration_parameters is not None:
        for parameter, parameter_value in configuration_parameters.items():
            if parameter not in added_params:
                command.extend(
                    [
                        "--{}".format(parameter),
                        parameter_value,
                    ]
                )
    if redis_arguments != "":
        redis_arguments_arr = redis_arguments.split(" ")
        logging.info(f"adding redis arguments {redis_arguments_arr}")
        command.extend(redis_arguments_arr)
    return command


def teardown_containers(redis_containers, container_type):
    for container in redis_containers:
        try:
            container.stop()
        except docker.errors.NotFound:
            logging.info(
                "When trying to stop {} container with id {} and image {} it was already stopped".format(
                    container_type, container.id, container.image
                )
            )
            pass


def spin_docker_standalone_redis(
    ceil_db_cpu_limit,
    current_cpu_pos,
    docker_client,
    redis_configuration_parameters,
    redis_containers,
    redis_proc_start_port,
    run_image,
    temporary_dir,
    password=None,
):
    mnt_point = "/mnt/redis/"
    command = generate_standalone_redis_server_args(
        "{}redis-server".format(mnt_point),
        redis_proc_start_port,
        mnt_point,
        redis_configuration_parameters,
        "",
        password,
    )
    command_str = " ".join(command)
    db_cpuset_cpus, current_cpu_pos = generate_cpuset_cpus(
        ceil_db_cpu_limit, current_cpu_pos
    )
    # Calculate nano_cpus for better CPU distribution
    redis_cpu_count = len(db_cpuset_cpus.split(","))
    redis_nano_cpus = int(redis_cpu_count * 1e9)  # 1 CPU = 1e9 nano_cpus

    logging.info(
        "Running redis-server on docker image {} (cpuset={}) with the following args: {}".format(
            run_image, db_cpuset_cpus, command_str
        )
    )
    logging.info(
        f"Redis container will use {redis_cpu_count} CPUs (nano_cpus={redis_nano_cpus}) on cores {db_cpuset_cpus}"
    )

    container = docker_client.containers.run(
        image=run_image,
        volumes={
            temporary_dir: {"bind": mnt_point, "mode": "rw"},
        },
        auto_remove=True,
        privileged=True,
        working_dir=mnt_point,
        command=command_str,
        network_mode="host",
        detach=True,
        cpuset_cpus=db_cpuset_cpus,
        nano_cpus=redis_nano_cpus,  # Force CPU distribution
        #  pid_mode="host",
    )
    redis_containers.append(container)
    return current_cpu_pos
