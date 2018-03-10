import scrapy
import re


class ChampionsLeagueSpider(scrapy.Spider):
    name = 'championsleaguespider'
    start_urls = ['https://www.uefa.com/uefachampionsleague/season=2018/clubs/']

    custom_settings = {
        'USER_AGENT': 'DDWcrawler',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 0.001,
    }

    # Parse statistics data of the current season
    def parse_phase(self, fields):
        phase = {}
        for field in fields:
            label = field.css('.statistics--list--label::text').extract_first()

            # Passing accuracy field
            if (label == 'passing accuracy'):
                value = field.css('.graph-circle--additional-text::text').extract_first()

            # Cards field
            elif (label == 'Cards'):
                cards = field.xpath('.//span[@class="statistics--list--data"]/text()').extract()
                labels = field.css('.statistics--list--data img::attr(title)').extract()

                yellow = re.findall('\d+', cards[0])
                red = re.findall('\d+', cards[1])

                value = {
                    labels[0].lower().replace(" ", "-"): yellow[0],
                    labels[1].lower().replace(" ", "-"): red[0],
                }

            # Passing types field
            elif (label == 'Passing types'):
                types = field.css('.statistics--list--data .graph-bar-container .bar-container')
                value = {}

                for type in types:
                    pass_type = type.css('span:not(.bar)::text').extract_first()
                    type_label = pass_type.split(' ')[1].lower()
                    type_value = type.css('span:not(.bar) b::text').extract_first() + ' ' + \
                                 pass_type.split(' ')[2]
                    value[type_label] = type_value

            # Goal types field
            elif (label == 'Type of goal'):
                types = field.css('.statistics--list--data .graph-dummy-container > div')
                value = {}
                for type in types:
                    type_label = type.xpath('.//span/text()').extract()
                    type_value = type.css('div > span::text').extract_first()
                    value[type_label[1].lower().replace(" ", "-")] = type_value

            # Standard fields
            else:
                value = field.css('.statistics--list--data::text').extract_first()

            phase[label.lower().replace(" ", "-")] = value

        return phase

    # Collect statistics data and split it into phases
    def parse_stats(self, response):
        player = response.meta['player']
        stats_sections = response.css('.player--statistics--list')
        player['matches'] = {}

        for section in stats_sections:
            fields = section.css('.field')
            phase_name = section.css('.stats-header::text').extract_first()

            # Tournament phase
            if (phase_name == 'Tournament phase'):
                player['matches']['tournament'] = self.parse_phase(fields)

            # Qualification phase
            elif (phase_name == 'Qualifying'):
                player['matches']['qualification'] = self.parse_phase(fields)

        yield player

    # Visit player's profile page, collect biography data and get a link to statistics page
    def parse_player(self, response):
        stats_url = response.css(
            '.content-wrap .section--footer a[title="More statistics"]::attr(href)').extract_first()

        for player in response.xpath('//div[@class="content-wrap"]'):
            bio = {
                'name': player.css('.player-header_name::text').extract_first(),
                'position': player.css('.player-header_category::text').extract_first(),
                'team': player.css('.player-header_team-name::text').extract_first(),
                'nationality': player.css('.player-header_country::text').extract_first(),
                'birthdate': player.css('.profile--list--data[itemprop=birthdate]::text').extract_first().split(' ')[0],
                'height': player.css('.profile--list--data[itemprop=height]::text').extract_first(),
                'weight': player.css('.profile--list--data[itemprop=weight]::text').extract_first(),
            }

            if (stats_url):
                yield scrapy.Request(response.urljoin(stats_url), callback=self.parse_stats, meta={'player': bio})
            else:
                yield bio

    # Visit page of each club and collect links to players profiles
    def parse_clubs(self, response):
        players = response.css('#team-data .squad--team-player')
        players_urls = players.css('.squad--player-name > a::attr(href)').extract()

        for player_url in players_urls:
            yield scrapy.Request(response.urljoin(player_url), callback=self.parse_player)

    # Get a list of clubs from the starting page
    def parse(self, response):
        clubs = response.css('.teams-overview_group .team > a')

        clubs_tocrawl = clubs.css('::attr(href)').extract()

        for club_url in clubs_tocrawl:
            yield scrapy.Request(response.urljoin(club_url), callback=self.parse_clubs)
