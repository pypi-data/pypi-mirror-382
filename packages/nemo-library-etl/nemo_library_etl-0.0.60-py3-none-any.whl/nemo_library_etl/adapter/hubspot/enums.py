from enum import Enum


class HubSpotLoadStep(Enum):
    PIPELINES = "Pipelines"
    DEALS = "Deals"
    DEAL_OWNERS = "DealOwners"
    DEAL_COMPANIES = "DealCompanies"
    COMPANY_DETAILS = "CompanyDetails"
    USERS = "Users"
    DEAL_HISTORY = "DealHistory"
    DEALS_WITH_HISTORY = "DealsWithHistory"
    JOINED_DEALS_WITH_HISTORY = "JoinedDealsWithHistory"
    DEALS_FORECAST_HEADER = "DealsForecastHeader"
    DEALS_FORECAST_DEALS = "DealsForecastDeals"
