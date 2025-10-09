import datetime as dt
import decimal as d
from abc import ABC
from dateutil.relativedelta import relativedelta


class BaseLslCalculator(ABC):
    """
    Abstract base class for Long Service Leave (LSL) calculators.

    This class provides default implementations for calculating LSL accrual,
    entitlement, and additional leave available on termination, based on
    continuous service and days not in service. It assumes a default accrual
    rate of 13 weeks every 15 years (or 8 2/3 weeks every 10 years), which is
    the most common rate in Australia.

    Methods
    -------
    calculate_accrual(as_at_date, continuous_service_date,
    days_not_in_service) -> Decimal
        Calculates the total LSL accrued as at a given date, based on service
        duration and the accrual rate.

    calculate_entitlement(as_at_date, continuous_service_date,
    days_not_in_service) -> Decimal
        Calculates the LSL entitlement as at a given date, with entitlements
        available at 10 years and every 5 years thereafter.

    additional_on_term(as_at_date, continuous_service_date,
        days_not_in_service) -> Decimal
        Calculates additional LSL available on termination, representing the
        accrual since the last entitlement.

    _protected _calculate_years_of_service_(as_at_date,
        continuous_service_date, days_not_in_service) -> float
        Calculates total years of service, excluding specified days not in
        service.

    _protected _accrual_rate_() -> float
        Returns the default accrual rate for LSL calculations.

    Parameters
    ----------
    as_at_date : datetime.date
        The date at which the entitlement or accrual is being calculated.
    continuous_service_date : datetime.date
        The date when the employee's continuous service started.
    days_not_in_service : int
        The number of days the employee was not in service during the period.

    Returns
    -------
    Decimal
        The calculated LSL accrual, entitlement, or additional leave in weeks.
    """

    def calculate_accrual(self, as_at_date: dt.date,
                          continuous_service_date: dt.date,
                          days_not_in_service: int) -> d.Decimal:
        """
        Default implementation for calculating LSL accrual.
        Calculated as accrual across the whole employment period at the
        accrual rate as per _accrual_rate_.

        :param as_at_date: The date at which the entitlement is being
            calculated.
        :param continuous_service_date: The date when the employee's
        continuous service started.
        :param days_not_in_service: The number of days the employee was not in
        service during the period.
        :return: The LSL accrual in weeks.
        """
        if continuous_service_date > as_at_date:
            return d.Decimal(0)

        # Calculate total service duration in years, excluding days not in
        # service
        years_of_service = self._calculate_years_of_service_(
            as_at_date,
            continuous_service_date,
            days_not_in_service)

        accrual = self._calculate_from_years_of_service_(years_of_service)

        return d.Decimal(accrual)

    def calculate_entitlement(self, as_at_date: dt.date,
                              continuous_service_date: dt.date,
                              days_not_in_service: int) -> d.Decimal:
        """
        Calculates the Long Service Leave (LSL) entitlement for an employee as
        of a given date.

        The entitlement is first available at 10 years of continuous service
        and then accrues every 5 years thereafter, using the accrual rate
        returned by the `_accrual_rate_` method. Days not in service are
        excluded from the calculation.

        Args:
            as_at_date (datetime.date): The date at which the entitlement is
            being calculated.
            continuous_service_date (datetime.date): The date when the
            employee's continuous service started.
            days_not_in_service (int): The number of days the employee was not
            in service during the period.

        Returns:
            decimal.Decimal: The calculated LSL entitlement in weeks. Returns 0
            if less than 10 years of service.
        """
        if continuous_service_date > as_at_date:
            return d.Decimal(0)

        # Calculate total service duration in years, excluding days not in
        # service
        years_of_service = self._calculate_years_of_service_(
            as_at_date,
            continuous_service_date,
            days_not_in_service)

        # Round down to the nearest multiple of 5
        rounded_years_of_service = int(years_of_service // 5) * 5

        if rounded_years_of_service < 10:
            return d.Decimal(0)

        # Calculate entitlement
        entitlement = self._calculate_from_years_of_service_(
            rounded_years_of_service)

        return d.Decimal(entitlement)

    def calculate_additional_on_term(self, as_at_date: dt.date,
                                     continuous_service_date: dt.date,
                                     days_not_in_service: int) -> d.Decimal:
        """
        Calculates the additional Long Service Leave (LSL) available upon
        termination.

        This method computes the difference between the total LSL accrued and
        the total LSL entitlement as of the given date.
        It is intended to be used when an employee's service is terminated, to
        determine any extra LSL that may be available.

        Args:
            as_at_date (datetime.date): The date at which the calculation is
            performed.
            continuous_service_date (datetime.date): The start date of
            continuous service.
            days_not_in_service (int): The number of days not counted as
            service.

        Returns:
            decimal.Decimal: The additional LSL available on termination,
            rounded to 4 decimal places.
        """
        if continuous_service_date > as_at_date:
            return d.Decimal(0)

        accrual = self.calculate_accrual(
            as_at_date, continuous_service_date, days_not_in_service)
        entitlement = self.calculate_entitlement(
            as_at_date, continuous_service_date, days_not_in_service)

        return d.Decimal(round(accrual, 4) - round(entitlement, 4))

    def _calculate_years_of_service_(self, as_at_date: dt.date,
                                     continuous_service_date: dt.date,
                                     days_not_in_service: int) -> float:
        """
        Calculates the total years of service for an employee, excluding
        specified days not in service.

        Args:
            as_at_date (datetime.date): The date up to which years of service
            are calculated.
            continuous_service_date (datetime.date): The date when continuous
            service began.
            days_not_in_service (int): The number of days to exclude from the
            service period.

        Returns:
            float: The total years of service, accounting for excluded days.
        """
        # add days not in service to continuous service date
        calc_start_date = continuous_service_date + dt.timedelta(
            days=days_not_in_service
        )

        # Calculate years between the calculated start date and the as_at_date
        date_delta = relativedelta(as_at_date, calc_start_date)
        years_of_service = (date_delta.years + (date_delta.months / 12) +
                            (date_delta.days / 365.25))

        return years_of_service

    def _calculate_from_years_of_service_(self, years_of_service: float) \
            -> float:
        """
        Calculates the total LSL accrued based on years of service and the
        accrual rate.

        Args:
            years_of_service (float): The total years of service.

        Returns:
            float: The total LSL accrued in weeks.
        """
        return round(years_of_service * self._accrual_rate_(), 4)

    def _accrual_rate_(self) -> float:
        """
        Returns the default long service leave accrual rate, calculated as 13
        weeks per 15 years (or equivalently, 8 2/3 weeks per 10 years), which
        is the most common accrual rate in Australia.

        Returns:
            float: The accrual rate as weeks per year.
        """
        return 13 / 15
