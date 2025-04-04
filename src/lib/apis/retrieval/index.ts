import { RETRIEVAL_API_BASE_URL } from '$lib/constants';
import { apiFetch } from '$lib/utils/apiClient';
export const getRAGConfig = async () => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/config`, { method: 'GET' });
};

type ChunkConfigForm = {
	chunk_size: number;
	chunk_overlap: number;
};

type ContentExtractConfigForm = {
	engine: string;
	tika_server_url: string | null;
};

type YoutubeConfigForm = {
	language: string[];
	translation?: string | null;
	proxy_url: string;
};

type RAGConfigForm = {
	pdf_extract_images?: boolean;
	enable_google_drive_integration?: boolean;
	chunk?: ChunkConfigForm;
	content_extraction?: ContentExtractConfigForm;
	web_loader_ssl_verification?: boolean;
	youtube?: YoutubeConfigForm;
};

export const updateRAGConfig = async (payload: RAGConfigForm) => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/config/update`, {
		method: 'POST',
		body: JSON.stringify({
			...payload
		})
	});
};

interface RagTemplateResponse {
	template: string;
}

export const getRAGTemplate = async () => {
	const res = await apiFetch<RagTemplateResponse>(`${RETRIEVAL_API_BASE_URL}/template`, {
		method: 'GET'
	});

	return res?.template ?? '';
};

export const getQuerySettings = async () => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/query/settings`, { method: 'GET' });
};

type QuerySettings = {
	k: number | null;
	r: number | null;
	template: string | null;
};

export const updateQuerySettings = async (settings: QuerySettings) => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/query/settings/update`, {
		method: 'POST',
		body: JSON.stringify({
			...settings
		})
	});
};

export const getEmbeddingConfig = async () => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/embedding`, { method: 'GET' });
};

type OpenAIConfigForm = {
	key: string;
	url: string;
};

type EmbeddingModelUpdateForm = {
	openai_config?: OpenAIConfigForm;
	embedding_engine: string;
	embedding_model: string;
	embedding_batch_size?: number;
};

export const updateEmbeddingConfig = async (payload: EmbeddingModelUpdateForm) => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/embedding/update`, {
		method: 'POST',
		body: JSON.stringify({
			...payload
		})
	});
};

export const getRerankingConfig = async () => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/reranking`, { method: 'GET' });
};

type RerankingModelUpdateForm = {
	reranking_model: string;
};

export const updateRerankingConfig = async (payload: RerankingModelUpdateForm) => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/reranking/update`, {
		method: 'POST',
		body: JSON.stringify({
			...payload
		})
	});
};

export interface SearchDocument {
	status: boolean;
	collection_name: string;
	filenames: string[];
}

export const processFile = async (file_id: string, collection_name: string | null = null) => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/process/file`, {
		method: 'POST',
		body: JSON.stringify({
			file_id: file_id,
			collection_name: collection_name ? collection_name : undefined
		})
	});
};

export const processYoutubeVideo = async (url: string) => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/process/youtube`, {
		method: 'POST',
		body: JSON.stringify({
			url: url
		})
	});
};

export const processWeb = async (collection_name: string, url: string) => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/process/web`, {
		method: 'POST',
		body: JSON.stringify({
			url: url,
			collection_name: collection_name
		})
	});
};

export const processWebSearch = async (
	query: string,
	collection_name?: string
): Promise<SearchDocument | null> => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/process/web/search`, {
		method: 'POST',
		body: JSON.stringify({
			query,
			collection_name: collection_name ?? ''
		})
	});
};

export const queryDoc = async (collection_name: string, query: string, k: number | null = null) => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/query/doc`, {
		method: 'POST',
		body: JSON.stringify({
			collection_name: collection_name,
			query: query,
			k: k
		})
	});
};

export const queryCollection = async (
	collection_names: string,
	query: string,
	k: number | null = null
) => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/query/collection`, {
		method: 'POST',
		body: JSON.stringify({
			collection_names: collection_names,
			query: query,
			k: k
		})
	});
};

export const resetUploadDir = async () => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/reset/uploads`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			authorization: `Bearer ${token}`
		}
	});
};

export const resetVectorDB = async () => {
	return await apiFetch(`${RETRIEVAL_API_BASE_URL}/reset/db`, {
		method: 'POST'
	});
};
