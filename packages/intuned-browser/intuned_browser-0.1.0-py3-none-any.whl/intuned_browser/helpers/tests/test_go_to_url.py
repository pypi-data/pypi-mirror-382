import os
from pathlib import Path

import pytest
from runtime import launch_chromium

from intuned_browser.helpers import go_to_url


def get_logs_dir() -> str:
    return os.path.join(os.path.dirname(Path(__file__).parent.parent), "run_results", "open_url_tests")


class TestOpenUrl:
    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.parametrize(
        "url",
        [
            "https://caleprocure.ca.gov/pages/LPASearch/lpa-search.aspx",
            # "https://www.rampla.org/s/opportunities",
            # "https://www.txsmartbuy.com/esbd",
            # "https://www.ptcvendorportal.com/#/sp/rfx-list?limit=10&page=1&order=-publishedDate&rfxNo=&rfxType=RFP&status=&title=&startDate=&endDate=",
            # "https://equalisgroup.org/purchasing-contracts/",
            # "https://www.biddingo.com/soundtransit",
            # "https://webapps1.dot.illinois.gov/WCTB/ConstructionSupportProcurementRequest/BulletinItems",
            # "https://www.commbuys.com/bso/view/search/external/advancedSearchBid.xhtml?q=MBTA&currentDocType=bids",
            # "https://www.commbuys.com/bso/view/search/external/advancedSearchBid.xhtml?q=DOT&currentDocType=bids",
            # "https://www.njstart.gov/bso/view/search/external/advancedSearchBid.xhtml?openBids=true",
            # "https://nevadaepro.com/bso/view/search/external/advancedSearchBid.xhtml?openBids=true",
        ],
    )
    async def test_slow_open_url(self, url: str):
        async with launch_chromium() as (_, page):
            await go_to_url(page=page, url=url)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.parametrize(
        "url",
        [
            "https://www.calpers.ca.gov/page/about/doing-business-with-calpers/bid-opportunities",
            # "https://www.energy.ca.gov/funding-opportunities/solicitations",
            # "https://mtc.bonfirehub.com/portal/?tab=openOpportunities",
            # "https://martabid.marta.net/CurrentOpportunities.aspx",
            # "https://bids.sciquest.com/apps/Router/PublicEvent?CustomerOrg=UGA",
            # "https://erms12c.indot.in.gov/INDOTBidViewer/BidOpportunities.aspx",
            # "https://bidopportunities.iowa.gov/",
            # "https://supplier.sok.ks.gov/psc/sokfsprdsup/SUPPLIER/ERP/c/SCP_PUBLIC_MENU_FL.SCP_PUB_BID_CMP_FL.GBL",
            # "http://webmail.dotd.louisiana.gov/AgreStat.nsf/BWebAdvertisements?OpenPage",
            # "https://osp.admin.mn.gov/PT-auto",
            # "https://mbid.ionwave.net/SourcingEvents.aspx?SourceType=1",
            # "https://ogs.ny.gov/procurement/bid-opportunities",
            # "https://otda.ny.gov/contracts/procurement-bid.asp",
            # "https://www.nyserda.ny.gov/Funding-Opportunities/Current-Funding-Opportunities",
            # "https://www.dasny.org/opportunities/rfps-bids",
            # "https://www.nyscr.ny.gov/",
            # "https://sucf.suny.edu/design-consulting-services/procurements-advertised",
            # "https://www.dot.ny.gov/doing-business/opportunities/consult-opportunities",
            # "https://comptroller.nyc.gov/services/for-businesses/doing-business-with-the-comptroller/rfps-solicitations/",
            # "https://www.ohioturnpike.org/business/doing-business-with-us/request-for-proposals",
            # "https://bids.sciquest.com/apps/Router/PublicEvent?CustomerOrg=TAMU",
            # "https://bids.sciquest.com/apps/Router/PublicEvent?CustomerOrg=MDAndersonPS",
            # "https://bids.sciquest.com/apps/Router/PublicEvent?CustomerOrg=StateOfUtah",
            # "https://www.mwaa.com/business/current-contracting-opportunities",
            # "https://bids.sciquest.com/apps/Router/PublicEvent?CustomerOrg=VATech",
        ],
    )
    async def test_fast_open_url(self, url: str):
        async with launch_chromium() as (_, page):
            await go_to_url(page=page, url=url)
