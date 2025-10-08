from .textrank.textrank_sentence import TextRankSentence
from loguru import logger


class SummarizeManager:
    @classmethod
    def summarize(cls, model_protocal: str, content: str) -> str:
        """
            文本摘要,支持的模型:
                1. local:textrank - 本地TextRank模型
        """
        if model_protocal.startswith('local:'):
            local_model = model_protocal.split(':')[1]
            if local_model == 'textrank':
                text_rank_model = TextRankSentence()
                text_rank_model.analyze(
                    text=content, lower=True, source='all_filters')
                items = text_rank_model.get_key_sentences(num=1)
                return items[0].sentence

        logger.warning(f"没有找到对应的摘要模型: {model_protocal}, 使用默认的内容返回")
        return content
