<%namespace name="markup" file="/helpers/markup.mako" />\
<?xml version="1.0" encoding="UTF-8" ?>

<feed xmlns="http://www.w3.org/2005/Atom">
    <id>tag:asb.dragonflycave.com,2015:feed</id>
    <title>The Cave of Dragonflies ASBdb news</title>
    <link href="${request.route_url('home')}" />
    <link rel="self" href="${request.route_url('news.feed')}" />

    <updated>${news[0].post_time.isoformat()}Z</updated>

    % for post in news:
        <entry>
            <id>tag:asb.dragonflycave.com,2015:news/${post.id}</id>
            <title>${post.title}</title>
            <link href="${
                request.resource_url(post.__parent__, post.identifier)
            }" />
            <published>${post.post_time.isoformat()}Z</published>
            <updated>${post.post_time.isoformat()}Z</updated>
            <author>
                <name>${post.poster.name}</name>
                <uri>${request.resource_url(
                    post.poster.__parent__, post.poster.identifier
                )}</uri>
            </author>

            <content type="html"><![CDATA[${
                markup.markup(post.text, post.format)
            }]]></content>
        </entry>
    % endfor
</feed>
