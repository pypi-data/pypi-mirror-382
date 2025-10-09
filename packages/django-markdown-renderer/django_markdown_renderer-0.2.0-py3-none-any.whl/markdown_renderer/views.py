from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.shortcuts import render
import json
import markdown2
import bleach

ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
    'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'hr', 'br',
    'img', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
    'del', 'sup', 'sub', 'input', 'details', 'summary', 'mark', 'kbd', 'iframe'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'alt', 'rel', 'target', 'dir'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'input': ['type', 'checked', 'disabled'],
    'iframe': ['src', 'allowfullscreen', 'webkitallowfullscreen', 'mozallowfullscreen', 'frameborder', 'width', 'height', 'style'],
    'p': ['dir'],
    '*': ['id', 'class', 'style']
}

class IndexView(TemplateView):
    template_name = 'markdown_renderer/index.html'

@csrf_exempt
def render_markdown(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        import re
        def align_table_cells(html, markdown):
            align_map = {}
            header_align = re.findall(r'<thead>.*?<tr>(.*?)</tr>.*?</thead>', html, re.DOTALL)
            if header_align:
                cells = re.findall(r'<th>(.*?)</th>', header_align[0])
                align_row = re.findall(r'\|([ :-]+)\|', markdown)
                if align_row:
                    aligns = [a.strip() for a in align_row[0].split('|') if a.strip()]
                    for i, a in enumerate(aligns):
                        if a.startswith(':') and a.endswith(':'):
                            align_map[i] = 'center'
                        elif a.endswith(':'):
                            align_map[i] = 'right'
                        elif a.startswith(':'):
                            align_map[i] = 'left'
            def add_align(m):
                idx = add_align.idx
                align = align_map.get(idx, None)
                add_align.idx += 1
                if align:
                    return m.group(0).replace('>', f' align="{align}">')
                return m.group(0)
            add_align.idx = 0
            html = re.sub(r'<th>', add_align, html)
            add_align.idx = 0
            html = re.sub(r'<td>', add_align, html)
            return html

        data = json.loads(request.body)
        markdown = str(data.get('markdown', ''))

        if not markdown:
            return JsonResponse({'error': 'markdown is required'}, status=400)

        if len(markdown) > 200_000:
            return JsonResponse({'error': 'markdown too large'}, status=413)

        html = markdown2.markdown(
            markdown,
            extras=[
                'fenced-code-blocks',
                'tables',
                'footnotes',
                'task_list',
                'strike',
                'cuddled-lists',
                'code-friendly',
                'header-ids',
                'metadata',
            ]
        )

        clean_html = bleach.clean(html,
                                tags=ALLOWED_TAGS,
                                attributes=ALLOWED_ATTRIBUTES,
                                strip=False)  # strip=False to keep empty tags like <img>

        # Replace [ ] and [x] task list items with real checkboxes
        def checkbox_replacer(match):
            checked = 'checked' if match.group(1).lower() == 'x' else ''
            return f"<input type='checkbox' disabled {checked}>"
        clean_html = re.sub(r'<li>\s*\[( |x|X)\]\s*', lambda m: '<li>' + checkbox_replacer(m), clean_html)

        # Table alignment post-processing
        clean_html = align_table_cells(clean_html, markdown)

        # Replace emoji shortcodes with Unicode emoji
        emoji_map = {
            ':smile:': '😄',
            ':rocket:': '🚀',
            ':heart:': '❤️',
            ':thumbsup:': '👍',
            ':fire:': '🔥',
            ':star:': '⭐',
            ':100:': '💯',
            ':clap:': '👏',
            ':eyes:': '👀',
            ':wave:': '👋',
            ':tada:': '🎉',
            ':thinking:': '🤔',
            ':sunglasses:': '😎',
            ':cry:': '😢',
            ':grin:': '😁',
            ':wink:': '😉',
            ':ok_hand:': '👌',
            ':pray:': '🙏',
            ':confetti_ball:': '🎊',
            ':poop:': '💩',
            ':blush:': '😊',
            ':angry:': '😠',
            ':sleeping:': '😴',
            ':zzz:': '💤',
            ':no_mouth:': '😶',
            ':neutral_face:': '😐',
            ':joy:': '😂',
            ':sob:': '😭',
            ':facepalm:': '🤦',
            ':muscle:': '💪',
            ':skull:': '💀',
            ':alien:': '👽',
            ':robot:': '🤖',
            ':cat:': '🐱',
            ':dog:': '🐶',
            ':sun:': '☀️',
            ':moon:': '🌙',
            ':rainbow:': '🌈',
            ':rose:': '🌹',
            ':crown:': '👑',
            ':gift:': '🎁',
            ':balloon:': '🎈',
            ':cake:': '🍰',
            ':coffee:': '☕',
            ':pizza:': '🍕',
            ':soccer:': '⚽',
            ':basketball:': '🏀',
            ':car:': '🚗',
            ':airplane:': '✈️',
            ':phone:': '📱',
            ':computer:': '💻',
            ':moneybag:': '💰',
            ':gem:': '💎',
            ':warning:': '⚠️',
            ':checkered_flag:': '🏁',
            ':medal:': '🏅',
            ':trophy:': '🏆',
        }
        for code, emoji in emoji_map.items():
            clean_html = clean_html.replace(code, emoji)

        # Replace @username with span for mention
        clean_html = re.sub(r'@([\w\-]+)', r'<span class="mention">@\1</span>', clean_html)

        return JsonResponse({'html': clean_html})

    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': 'render failed'}, status=500)

    try:
        data = json.loads(request.body)
        markdown = str(data.get('markdown', ''))

        if not markdown:
            return JsonResponse({'error': 'markdown is required'}, status=400)

        if len(markdown) > 200_000:
            return JsonResponse({'error': 'markdown too large'}, status=413)

        # Convert Markdown to HTML
        html = markdown2.markdown(
            markdown,
            extras=[
                'fenced-code-blocks',
                'tables',
                'footnotes',
                'task_list',
                'strike',
                'cuddled-lists',
                'code-friendly',
                'header-ids',
                'metadata',
            ]
        )

        # Clean HTML
        clean_html = bleach.clean(html,
                                tags=ALLOWED_TAGS,
                                attributes=ALLOWED_ATTRIBUTES,
                                strip=True)

        # Replace [ ] and [x] task list items with real checkboxes
        import re
        def checkbox_replacer(match):
            checked = 'checked' if match.group(1).lower() == 'x' else ''
            return f"<input type='checkbox' disabled {checked}>"
        clean_html = re.sub(r'<li>\s*\[( |x|X)\]\s*', lambda m: '<li>' + checkbox_replacer(m), clean_html)

        # Replace emoji shortcodes with Unicode emoji
        emoji_map = {
            ':smile:': '😄',
            ':rocket:': '🚀',
        }
        for code, emoji in emoji_map.items():
            clean_html = clean_html.replace(code, emoji)

        # Replace @username with span for mention
        clean_html = re.sub(r'@([\w\-]+)', r'<span class="mention">@\1</span>', clean_html)

        return JsonResponse({'html': clean_html})

    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': 'render failed'}, status=500)

def health_check(request):
    return JsonResponse({'ok': True})
