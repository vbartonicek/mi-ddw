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

    def parse_stats(self, response):
        for stats in response.xpath('//div[@class="content-wrap"]'):

            player = response.meta['player']
            stats_sections = stats.css('.player--statistics--list')

            tournament = {}
            qualification = {}

            for section in stats_sections:
                fields = section.css('.field')

                # Tournament phase
                if (stats.css('.stats-header::text').extract_first() == 'Tournament phase'):
                    for field in fields:
                        label = field.css('.statistics--list--label::text').extract_first()

                        # Passing accuracy
                        if (label == 'passing accuracy'):
                            value = field.css('.graph-circle--additional-text::text').extract_first()

                        # Cards
                        elif (label == 'Cards'):
                            cards = field.xpath('.//span[@class="statistics--list--data"]/text()').extract()

                            yellow = re.findall('\d+', cards[0])
                            red = re.findall('\d+', cards[1])

                            value = {
                                'yellow': yellow[0],
                                'red': red[0],
                            }

                        # Passing types
                        elif (label == 'Passing types'):
                            types = field.css('.statistics--list--data .graph-bar-container .bar-container')
                            value = {}

                            for type in types:
                                pass_type = type.css('span:not(.bar)::text').extract_first()
                                type_label = pass_type.split(' ')[1].lower()
                                type_value = type.css('span:not(.bar) b::text').extract_first() + ' ' + \
                                             pass_type.split(' ')[2]
                                value[type_label] = type_value

                        # Goal types
                        elif (label == 'Type of goal'):
                            types = field.css('.statistics--list--data .graph-dummy-container > div')
                            value = {}
                            for type in types:
                                type_label = type.xpath('.//span/text()').extract()
                                type_value = type.css('div > span::text').extract_first()
                                value[type_label[1]] = type_value

                        else:
                            value = field.css('.statistics--list--data::text').extract_first()

                        tournament[label.lower().replace(" ", "-")] = value

                # Qualification phase
                elif (stats.css('.stats-header::text').extract_first() == 'Qualifying'):
                    for field in fields:
                        qualification[field.css('.statistics--list--label::text').extract_first()] = field.css(
                            '.statistics--list--data::text').extract_first()

        player['matches'] = {
            'tournament': tournament,
            'qualification:': qualification,
        }

        yield player

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

            yield scrapy.Request(response.urljoin(stats_url), callback=self.parse_stats, meta={'player': bio})

    def parse_clubs(self, response):
        players = response.css('#team-data .squad--team-player')
        players_urls = players.css('.squad--player-name > a::attr(href)').extract()

        for player_url in players_urls:
            yield scrapy.Request(response.urljoin(player_url), callback=self.parse_player)

    def parse(self, response):
        clubs = response.css('.team > a')

        clubs_tocrawl = clubs.css('::attr(href)').extract()

        for club_url in clubs_tocrawl:
            yield scrapy.Request(response.urljoin(club_url), callback=self.parse_clubs)
