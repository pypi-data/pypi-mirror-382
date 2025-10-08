#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##
# This file is part of the Open SDK
#
# Contributors:
#   - Sergio Giménez (sergio.gimenez@i2cat.net)
#   - César Cajas (cesar.cajas@i2cat.net)
##
import json
from typing import Optional

import requests
from pydantic import BaseModel

from sunrise6g_opensdk import logger
from sunrise6g_opensdk.edgecloud.adapters.errors import EdgeCloudPlatformError

log = logger.get_logger(__name__)


class I2EdgeError(EdgeCloudPlatformError):
    pass


class I2EdgeErrorResponse(BaseModel):
    message: str
    detail: dict


def get_error_message_from(response: requests.Response) -> str:
    try:
        error_response = I2EdgeErrorResponse(**response.json())
        return error_response.message
    except Exception as e:
        log.error("Failed to parse error response from i2edge: {}".format(e))
        return response.text


def i2edge_post(url: str, model_payload: BaseModel, expected_status: int = 201) -> dict:
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
    }
    json_payload = json.dumps(model_payload.model_dump(mode="json", exclude_none=True))

    # Debug: Log the payload being sent to i2Edge
    log.debug(f"Sending payload to i2Edge: {json_payload}")

    try:
        response = requests.post(url, data=json_payload, headers=headers)
        if response.status_code == expected_status:
            return response
        else:
            # Raise an error with meaningful message about status code mismatch
            i2edge_err_msg = get_error_message_from(response)
            err_msg = "Failed to post: Expected status {}, got {}. Detail: {}".format(
                expected_status, response.status_code, i2edge_err_msg
            )
            log.error(err_msg)
            raise I2EdgeError(err_msg)
    except requests.exceptions.HTTPError as e:
        i2edge_err_msg = get_error_message_from(response)
        err_msg = "Failed to deploy app: {}. Detail: {}".format(i2edge_err_msg, e)
        log.error(err_msg)
        raise I2EdgeError(err_msg)


def i2edge_patch(url: str, model_payload: BaseModel, expected_status: int = 200) -> dict:
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
    }
    json_payload = json.dumps(model_payload.model_dump(exclude_unset=True, mode="json"))
    try:
        response = requests.patch(url, data=json_payload, headers=headers)
        if response.status_code == expected_status:
            return response
        else:
            i2edge_err_msg = get_error_message_from(response)
            err_msg = "Failed to patch: Expected status {}, got {}. Detail: {}".format(
                expected_status, response.status_code, i2edge_err_msg
            )
            log.error(err_msg)
            raise I2EdgeError(err_msg)
    except requests.exceptions.HTTPError as e:
        i2edge_err_msg = get_error_message_from(response)
        err_msg = "Failed to patch: {}. Detail: {}".format(i2edge_err_msg, e)
        log.error(err_msg)
        raise I2EdgeError(err_msg)


def i2edge_post_multiform_data(url: str, model_payload: BaseModel) -> dict:
    headers = {
        "accept": "application/json",
    }
    payload_dict = model_payload.model_dump(mode="json")
    payload_in_str = {k: str(v) for k, v in payload_dict.items()}
    try:
        response = requests.post(url, data=payload_in_str, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        i2edge_err_msg = get_error_message_from(response)
        err_msg = "Failed to deploy app: {}. Detail: {}".format(i2edge_err_msg, e)
        log.error(err_msg)
        raise I2EdgeError(err_msg)


def i2edge_delete(url: str, id: str, expected_status: int = 200) -> dict:
    headers = {"accept": "application/json"}
    try:
        query = "{}/{}".format(url, id)
        response = requests.delete(query, headers=headers)
        if response.status_code == expected_status:
            return response
        else:
            # Raise an error with meaningful message about status code mismatch
            i2edge_err_msg = get_error_message_from(response)
            err_msg = "Failed to delete: Expected status {}, got {}. Detail: {}".format(
                expected_status, response.status_code, i2edge_err_msg
            )
            log.error(err_msg)
            raise I2EdgeError(err_msg)
    except requests.exceptions.HTTPError as e:
        i2edge_err_msg = get_error_message_from(response)
        err_msg = "Failed to undeploy app: {}. Detail: {}".format(i2edge_err_msg, e)
        log.error(err_msg)
        raise I2EdgeError(err_msg)


def i2edge_get(url: str, params: Optional[dict], expected_status: int = 200):
    headers = {"accept": "application/json"}
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == expected_status:
            return response
        else:
            # Raise an error with meaningful message about status code mismatch
            i2edge_err_msg = get_error_message_from(response)
            err_msg = "Failed to get: Expected status {}, got {}. Detail: {}".format(
                expected_status, response.status_code, i2edge_err_msg
            )
            log.error(err_msg)
            raise I2EdgeError(err_msg)
    except requests.exceptions.HTTPError as e:
        i2edge_err_msg = get_error_message_from(response)
        err_msg = "Failed to get apps: {}. Detail: {}".format(i2edge_err_msg, e)
        log.error(err_msg)
        raise I2EdgeError(err_msg)
