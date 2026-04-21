AI共创社区
=============

AI资源互助平台 - 点子共享，实践落地

功能特性
--------

- **点子广场**: 发布和浏览 AI 点子，寻找志同道合的伙伴
- **资源库**: 分享模型、数据集、工具、API 等资源
- **互助匹配**: 通过标签匹配点子和资源
- **AI 助手**: 集成 GPT4Free，帮助生成和优化点子

安装
----

.. code-block:: bash

    pip install -e ".[testing]"

配置
----

在 ``development.ini`` 中添加::

    kotti.configurators =
        kotti_ai_community.kotti_configure

    kotti.available_types =
        kotti_ai_community.resources.Idea
        kotti_ai_community.resources.ResourceItem
