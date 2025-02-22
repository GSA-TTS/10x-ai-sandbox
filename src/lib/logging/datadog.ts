import { datadogRum } from '@datadog/browser-rum';
import { datadogLogs } from '@datadog/browser-logs';
import { dev } from '$app/environment';

import {
	PUBLIC_DATADOG_APP_ID,
	PUBLIC_DATADOG_CLIENT_TOKEN,
	PUBLIC_DATADOG_BROWSERLOGS_CLIENT_TOKEN,
	PUBLIC_DATADOG_SERVICE
} from '$env/static/public';

const env = dev ? 'dev' : 'prod';

export function initDataDog() {
	if (!PUBLIC_DATADOG_APP_ID || !PUBLIC_DATADOG_CLIENT_TOKEN) {
		return;
	}
	datadogRum.init({
		applicationId: PUBLIC_DATADOG_APP_ID,
		clientToken: PUBLIC_DATADOG_CLIENT_TOKEN,
		// `site` refers to the Datadog site parameter of your organization
		// see https://docs.datadoghq.com/getting_started/site/
		site: 'ddog-gov.com',
		service: PUBLIC_DATADOG_SERVICE,
		env: env,
		// Specify a version number to identify the deployed version of your application in Datadog
		// version: '1.0.0',
		sessionSampleRate: 100,
		sessionReplaySampleRate: 20,
		defaultPrivacyLevel: 'mask-user-input'
	});
	datadogLogs.init({
		clientToken: PUBLIC_DATADOG_BROWSERLOGS_CLIENT_TOKEN,
		site: 'ddog-gov.com',
		forwardErrorsToLogs: true,
		sessionSampleRate: 100
	});
}
