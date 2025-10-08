[![Build Status](https://travis-ci.com/uw-it-aca/admissions-cohort-manager.svg?branch=master)](https://travis-ci.com/uw-it-aca/admissions-cohort-manager) [![Coverage Status](https://coveralls.io/repos/github/uw-it-aca/uw-restclients-adsel/badge.svg?branch=master)](https://coveralls.io/github/uw-it-aca/uw-restclients-adsel?branch=master)
# REST client for AdSel

Installation:

    pip install UW-RestClients-AdSel

To use this client, you'll need these settings in your application or script:

    # Specifies whether requests should use live or mocked resources,
    # acceptable values are 'Live' or 'Mock' (default)
    RESTCLIENTS_ADSEL_DAO_CLASS='Live'

    # Paths to UWCA cert and key files
    RESTCLIENTS_ADSEL_CERT_FILE='/path/to/cert'
    RESTCLIENTS_ADSEL_KEY_FILE='/path/to/key'

    # AdSel REST API hostname (eval or production)
    RESTCLIENTS_ADSEL_HOST='https://zoom.com'

Optional settings:

    # Customizable parameters for urllib3
    RESTCLIENTS_ADSEL_TIMEOUT=5
    RESTCLIENTS_ADSEL_POOL_SIZE=10

See examples for usage.  Pull requests welcome.
