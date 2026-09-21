#!/usr/bin/env bash
function tkbuild() {
    local project_id=kuohwa
    while getopts "p" opt; do
        case $opt in
            l) local disable_cache_from_image="true" ;;
        esac
    done
    if ! [ -f Dockerfile ]; then
        echo "Dockerfile not found"
        return 1
    fi
    local component=${PWD##*/}
    local lookup_path=$(dirname ${PWD})
    while [ ! -d ${lookup_path}/.git ] && [ "$(dirname ${lookup_path})" != "${lookup_path}" ]; do
        local component=${lookup_path##*/}-${component}
        local lookup_path=$(dirname ${lookup_path})
    done
    if [ "${component}" == "" ]; then
        echo "Not a component: ${PWD}"
        return 1
    fi
    local extra_command=""
    if [ "${disable_cache_from_image}" != "true" ]; then
        local extra_command="${extra_command} --cache-from asia.gcr.io/${project_id}/${component}:develop"
    fi
    # gcloud auth configure-docker asia.gcr.io
    docker pull asia.gcr.io/${project_id}/${component}:develop 2>/dev/null || true
    if docker build -t asia.gcr.io/${project_id}/${component}:develop \
            --build-arg PROJECT_ID=${project_id} --build-arg VERSION=develop \
            ${extra_command} .; then
        docker push asia.gcr.io/${project_id}/${component}:develop
    fi
    return 0
}
function tkrun() {
    local project_id=kuohwa
    local component=${PWD##*/}
    local lookup_path=$(dirname ${PWD})
    while [ ! -d ${lookup_path}/.git ] && [ "$(dirname ${lookup_path})" != "${lookup_path}" ]; do
        local component=${lookup_path##*/}-${component}
        local lookup_path=$(dirname ${lookup_path})
    done
    if [ "${component}" == "" ]; then
        echo "Not a component: ${PWD}"
        return 1
    fi
    docker run -it --rm \
        -v "${KUBECONFIG}":/etc/kubernetes/admin.conf:ro \
        -e KUBECONFIG=/etc/kubernetes/admin.conf \
        asia.gcr.io/${project_id}/${component}:develop "$@"
}
