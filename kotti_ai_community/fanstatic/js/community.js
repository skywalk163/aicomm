// AI共创社区 JavaScript

$(document).ready(function() {
    // 标签输入处理
    $('input[name="tags"]').on('blur', function() {
        var value = $(this).val();
        // 清理标签格式
        if (value) {
            var tags = value.split(/[,，]/).map(function(tag) {
                return tag.trim();
            }).filter(function(tag) {
                return tag.length > 0;
            });
            $(this).val(tags.join(', '));
        }
    });

    // 点赞功能
    $('.btn-like').on('click', function(e) {
        e.preventDefault();
        var btn = $(this);
        var url = btn.data('url');
        var countSpan = btn.find('.like-count');
        
        $.post(url, function(data) {
            if (data.success) {
                countSpan.text(data.count);
                btn.toggleClass('btn-default btn-primary');
            }
        });
    });

    // 关注功能
    $('.btn-follow').on('click', function(e) {
        e.preventDefault();
        var btn = $(this);
        var url = btn.data('url');
        
        $.post(url, function(data) {
            if (data.success) {
                if (data.following) {
                    btn.text('已关注').removeClass('btn-primary').addClass('btn-success');
                } else {
                    btn.text('关注').removeClass('btn-success').addClass('btn-primary');
                }
            }
        });
    });

    // 搜索框自动完成
    $('input[name="search"]').on('input', function() {
        var query = $(this).val();
        if (query.length >= 2) {
            // TODO: 实现搜索建议
        }
    });

    // 分类筛选联动
    $('select[name="category"]').on('change', function() {
        $(this).closest('form').submit();
    });
});
