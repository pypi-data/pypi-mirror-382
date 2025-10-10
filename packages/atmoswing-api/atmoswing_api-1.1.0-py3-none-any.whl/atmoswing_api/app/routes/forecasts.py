import logging
from typing import List
from functools import lru_cache
from fastapi import APIRouter, HTTPException, Depends, Query
from typing_extensions import Annotated

from atmoswing_api import config
from atmoswing_api.cache import *
from atmoswing_api.app.models.models import *
from atmoswing_api.app.services.forecasts import *

router = APIRouter()
debug = False


@lru_cache
def get_settings():
    return config.Settings()


# Helper function to handle requests and catch exceptions
async def _handle_request(func, settings: config.Settings, region: str, **kwargs):
    try:
        result = await func(settings.data_dir, region, **kwargs)
        if debug:
            logging.info(f"Result from {func.__name__}: {result}")
        if result is None:
            raise ValueError("The result is None")
        return result
    except FileNotFoundError as e:
        logging.error(f"Files not found for region: {region} "
                      f"(directory: {settings.data_dir})")
        logging.error(f"Error details: {e}")
        raise HTTPException(status_code=400, detail=f"Region or forecast not found ({e})")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error ({e})")


@router.get("/{region}/{forecast_date}/{method}/{configuration}/{lead_time}/analog-dates",
            summary="Analog dates for a given forecast and target date",
            response_model=AnalogDatesResponse,
            response_model_exclude_none=True)
@redis_cache(ttl=3600)
async def analog_dates(
        region: str,
        forecast_date: str,
        method: str,
        configuration: str,
        lead_time: int|str,
        settings: Annotated[config.Settings, Depends(get_settings)]):
    """
    Get the analog dates for a given region, forecast date, method, configuration, and lead time.
    """
    return await _handle_request(get_analog_dates, settings, region,
                                 forecast_date=forecast_date, method=method,
                                 configuration=configuration, lead_time=lead_time)


@router.get("/{region}/{forecast_date}/{method}/{configuration}/{lead_time}/analogy-criteria",
            summary="Analog criteria for a given forecast and target date",
            response_model=AnalogCriteriaResponse,
            response_model_exclude_none=True)
@redis_cache(ttl=3600)
async def analog_criteria(
        region: str,
        forecast_date: str,
        method: str,
        configuration: str,
        lead_time: int|str,
        settings: Annotated[config.Settings, Depends(get_settings)]):
    """
    Get the analog criteria for a given region, forecast date, method, configuration, and lead time.
    """
    return await _handle_request(get_analog_criteria, settings, region,
                                 forecast_date=forecast_date, method=method,
                                 configuration=configuration, lead_time=lead_time)


@router.get("/{region}/{forecast_date}/{method}/{configuration}/{lead_time}/entities-values-percentile/{percentile}",
            summary="Values for all entities for a given quantile, forecast and target date",
            response_model=EntitiesValuesPercentileResponse,
            response_model_exclude_none=True)
@redis_cache(ttl=3600)
async def entities_analog_values_percentile(
        region: str,
        forecast_date: str,
        method: str,
        configuration: str,
        lead_time: int|str,
        percentile: int,
        settings: Annotated[config.Settings, Depends(get_settings)],
        normalize: int = Query(10)):
    """
    Get the precipitation values for a given region, forecast date, method, configuration, lead time, and percentile.
    """
    return await _handle_request(get_entities_analog_values_percentile, settings, region,
                                 forecast_date=forecast_date, method=method,
                                 configuration=configuration, lead_time=lead_time,
                                 percentile=percentile, normalize=normalize)


@router.get("/{region}/{forecast_date}/{method}/{configuration}/{entity}/reference-values",
            summary="Reference values (e.g. for different return periods) for a given entity",
            response_model=ReferenceValuesResponse,
            response_model_exclude_none=True)
@redis_cache(ttl=3600)
async def reference_values(
        region: str,
        forecast_date: str,
        method: str,
        configuration: str,
        entity: int,
        settings: Annotated[config.Settings, Depends(get_settings)]):
    """
    Get the reference values for a given region, forecast date, method, configuration, and entity.
    """
    return await _handle_request(get_reference_values, settings, region,
                                 forecast_date=forecast_date, method=method,
                                 configuration=configuration, entity=entity)


@router.get("/{region}/{forecast_date}/{method}/{configuration}/{entity}/series-values-best-analogs",
            summary="Analog values of the best analogs for a given entity (time series)",
            response_model=SeriesAnalogValuesResponse,
            response_model_exclude_none=True)
@redis_cache(ttl=3600)
async def series_analog_values_best(
        region: str,
        forecast_date: str,
        method: str,
        configuration: str,
        entity: int,
        settings: Annotated[config.Settings, Depends(get_settings)],
        number: int = 10):
    """
    Get the precipitation values for the best analogs and for a given region, forecast date, method, configuration, and entity.
    """
    return await _handle_request(get_series_analog_values_best, settings, region,
                                 forecast_date=forecast_date, method=method,
                                 configuration=configuration, entity=entity,
                                 number=number)


@router.get("/{region}/{forecast_date}/{method}/{configuration}/{entity}/series-values-percentiles",
            summary="Values for one entity for a given quantile, forecast and target date",
            response_model=SeriesValuesPercentilesResponse,
            response_model_exclude_none=True)
@redis_cache(ttl=3600)
async def series_analog_values_percentiles(
        region: str,
        forecast_date: str,
        method: str,
        configuration: str,
        entity: int,
        settings: Annotated[config.Settings, Depends(get_settings)],
        percentiles: List[int] = Query([20, 60, 90])):
    """
    Get the precipitation values for the provided percentiles and for a given region, forecast date, method, configuration, and entity.
    """
    return await _handle_request(get_series_analog_values_percentiles, settings, region,
                                 forecast_date=forecast_date, method=method,
                                 configuration=configuration, entity=entity,
                                 percentiles=percentiles)


@router.get("/{region}/{forecast_date}/{method}/{configuration}/{entity}/series-values-percentiles-history",
            summary="Values from the past forecasts for one entity, a given quantile and target date",
            response_model=SeriesValuesPercentilesHistoryResponse,
            response_model_exclude_none=True)
@redis_cache(ttl=3600)
async def series_analog_values_percentiles_history(
        region: str,
        forecast_date: str,
        method: str,
        configuration: str,
        entity: int,
        settings: Annotated[config.Settings, Depends(get_settings)],
        percentiles: List[int] = Query([20, 60, 90]),
        number: int = 5):
    """
    Get the precipitation values for the provided percentiles and for a given region, forecast date, method, configuration, and entity.
    """
    return await _handle_request(get_series_analog_values_percentiles_history, settings,
                                 region, forecast_date=forecast_date, method=method,
                                 configuration=configuration, entity=entity,
                                 percentiles=percentiles, number=number)


@router.get("/{region}/{forecast_date}/{method}/{configuration}/{entity}/{lead_time}/analogs",
            summary="Details of the analogs (rank, date, criteria, value) for a given forecast and entity",
            response_model=AnalogsResponse,
            response_model_exclude_none=True)
@redis_cache(ttl=3600)
async def analogs(
        region: str,
        forecast_date: str,
        method: str,
        configuration: str,
        entity: int,
        lead_time: int|str,
        settings: Annotated[config.Settings, Depends(get_settings)]):
    """
    Get the analogs for a given region, forecast date, method, configuration, entity, and lead time.
    """
    return await _handle_request(get_analogs, settings, region,
                                 forecast_date=forecast_date, method=method,
                                 configuration=configuration, entity=entity,
                                 lead_time=lead_time)


@router.get("/{region}/{forecast_date}/{method}/{configuration}/{entity}/{lead_time}/analog-values",
            summary="Analog values for a given entity and target date",
            response_model=AnalogValuesResponse,
            response_model_exclude_none=True)
@redis_cache(ttl=3600)
async def analog_values(
        region: str,
        forecast_date: str,
        method: str,
        configuration: str,
        entity: int,
        lead_time: int|str,
        settings: Annotated[config.Settings, Depends(get_settings)]):
    """
    Get the precipitation values for a given region, forecast date, method, configuration, entity, lead time.
    """
    return await _handle_request(get_analog_values, settings, region,
                                 forecast_date=forecast_date, method=method,
                                 configuration=configuration, entity=entity,
                                 lead_time=lead_time)


@router.get("/{region}/{forecast_date}/{method}/{configuration}/{entity}/{lead_time}/analog-values-percentiles",
            summary="Values for one entity for a given quantile, forecast and target date",
            response_model=AnalogValuesPercentilesResponse,
            response_model_exclude_none=True)
@redis_cache(ttl=3600)
async def analog_values_percentiles(
        region: str,
        forecast_date: str,
        method: str,
        configuration: str,
        entity: int,
        lead_time: int|str,
        settings: Annotated[config.Settings, Depends(get_settings)],
        percentiles: List[int] = Query([20, 60, 90])):
    """
    Get the precipitation values for a given region, forecast date, method, configuration, entity, lead time, and percentile.
    """
    return await _handle_request(get_analog_values_percentiles, settings, region,
                                 forecast_date=forecast_date, method=method,
                                 configuration=configuration, entity=entity,
                                 lead_time=lead_time, percentiles=percentiles)


@router.get("/{region}/{forecast_date}/{method}/{configuration}/{entity}/{lead_time}/analog-values-best",
            summary="Values for one entity for a given quantile, forecast and target date",
            response_model=AnalogValuesResponse,
            response_model_exclude_none=True)
@redis_cache(ttl=3600)
async def analog_values_best(
        region: str,
        forecast_date: str,
        method: str,
        configuration: str,
        entity: int,
        lead_time: int|str,
        settings: Annotated[config.Settings, Depends(get_settings)],
        number: int = 10):
    """
    Get the precipitation values for the best analogs and for a given region, forecast date, method, configuration, entity, and lead time.
    """
    return await _handle_request(get_analog_values_best, settings, region,
                                 forecast_date=forecast_date, method=method,
                                 configuration=configuration, entity=entity,
                                 lead_time=lead_time, number=number)