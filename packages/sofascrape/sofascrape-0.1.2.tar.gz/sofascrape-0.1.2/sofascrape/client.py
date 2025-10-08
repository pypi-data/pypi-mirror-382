from playwright.sync_api import sync_playwright, TimeoutError
import logging
import json
from bs4 import BeautifulSoup
import inspect
import csv
import os
from typing import Union, Optional

class ApiResponse:
    """
    Wrapper for API responses that provides save functionality
    """
    def __init__(self, data: Union[dict, list], client: 'SofascoreClient'):
        self.data = data
        self.client = client
        
    def json(self, path: Optional[str] = None) -> str:
        """
        Save response data as JSON file
        
        Args:
            path: Optional custom path for the file
            
        Returns:
            Path to the saved file
        """
        filename = path or f"{self.client._get_current_function_name()}.json"
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
            
        return filename
        
    def csv(self, path: Optional[str] = None) -> str:
        """
        Save response data as CSV file
        
        Args:
            path: Optional custom path for the file
            
        Returns:
            Path to the saved file
        """
        filename = path or f"{self.client._get_current_function_name()}.csv"
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if isinstance(self.data, list) and self.data:
                # Handle list of dictionaries
                if isinstance(self.data[0], dict):
                    writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                    writer.writeheader()
                    writer.writerows(self.data)
                else:
                    # Handle list of non-dictionaries
                    writer = csv.writer(f)
                    writer.writerow(['value'])
                    for item in self.data:
                        writer.writerow([item])
            elif isinstance(self.data, dict):
                # Handle dictionary - flatten if needed
                writer = csv.writer(f)
                writer.writerow(['key', 'value'])
                for key, value in self.data.items():
                    writer.writerow([key, json.dumps(value) if isinstance(value, (dict, list)) else value])
            else:
                # Handle primitive types
                writer = csv.writer(f)
                writer.writerow(['value'])
                writer.writerow([self.data])
                    
        return filename
        
    def __getitem__(self, key):
        """Allow dictionary-like access to data"""
        return self.data[key]
        
    def __iter__(self):
        """Allow iteration over data"""
        return iter(self.data)
        
    def __len__(self):
        """Return length of data"""
        return len(self.data) if isinstance(self.data, (list, dict)) else 1
        
    def __repr__(self):
        return f"ApiResponse({self.data!r})"

class SofascoreClient:
    
    BASE_URL = "https://www.sofascore.com"
    
    def __init__(self, headless=True, timeout=30000):
        self.headless = headless
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def start(self):
        """Initialize the Playwright client"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            self.page.set_default_timeout(self.timeout)
        except Exception as e:
            logging.error(f"Failed to start Playwright client: {e}")
            self.close()
            raise
            
    def goto(self, url, timeout=None):
        """Navigate to a URL"""
        if not self.page:
            raise RuntimeError("Client not initialized. Call start() first or use context manager.")
            
        try:
            self.page.goto(url, timeout=timeout or self.timeout)
        except TimeoutError:
            raise TimeoutError(f"Navigation to {url} timed out after {timeout or self.timeout}ms")
        except Exception as e:
            raise RuntimeError(f"Failed to navigate to {url}: {e}")
            
    def get_content(self):
        """Get page content as JSON dict"""
        if not self.page:
            raise RuntimeError("Client not initialized. Call start() first or use context manager.")
            
        # Get raw HTML content
        html_content = self.page.content()
        
        # Parse HTML and extract JSON from <pre> tag
        soup = BeautifulSoup(html_content, 'html.parser')
        pre_tag = soup.find('pre')
        
        if pre_tag:
            try:
                # Convert JSON string to Python dict
                json_data = json.loads(pre_tag.text)
                return json_data
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON from page content: {e}")
        else:
            raise ValueError("No JSON data found in page content")
        
    def close(self):
        """Clean up resources"""
        if self.page:
            self.page.close()
            self.page = None
            
        if self.context:
            self.context.close()
            self.context = None
            
        if self.browser:
            self.browser.close()
            self.browser = None
            
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
            
    def get_page_content(self, url, timeout=None):
        """Navigate to URL and return page content as ApiResponse"""
        self.goto(url, timeout)
        data = self.get_content()
        return ApiResponse(data, self)

    def _get_current_function_name(self) -> str:
        """Get the name of the calling function"""
        current_frame = inspect.currentframe()
        if current_frame is None:
            return "unknown_function"
        caller_frame = current_frame.f_back
        if caller_frame is None:
            return "unknown_function"
        return caller_frame.f_code.co_name
    
    # API endpoint methods
    def get_sport_event_count(self, sport_id):
        """Get event count for a specific sport"""
        url = f"{self.BASE_URL}/api/v1/sport/{sport_id}/event-count"
        return self.get_page_content(url)
    
    def get_event_ai_insights(self, event_id, language="en"):
        """Get AI-generated match insights for a specific event"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/ai-insights/{language}"
        return self.get_page_content(url)
    
    def get_event_incidents(self, event_id):
        """Get incidents for a specific event"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/incidents"
        return self.get_page_content(url)
    
    def get_event_pregame_form(self, event_id):
        """Get pregame form for a specific event"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/pregame-form"
        return self.get_page_content(url)
    
    def get_event_h2h(self, event_id):
        """Get head-to-head data for a specific event"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/h2h"
        return self.get_page_content(url)
    
    def get_event_managers(self, event_id):
        """Get managers for a specific event"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/managers"
        return self.get_page_content(url)
    
    def get_event_tv_channels(self, event_id, country_code):
        """Get TV channels for a specific event in a country"""
        url = f"{self.BASE_URL}/api/v1/tv/event/{event_id}/country-channels"
        return self.get_page_content(url)
    
    def get_team_featured_players(self, team_id):
        """Get featured players for a specific team"""
        url = f"{self.BASE_URL}/api/v1/team/{team_id}/featured-players"
        return self.get_page_content(url)
    
    def get_event_win_probability(self, event_id):
        """Get win probability graph data for a specific event"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/graph/win-probability"
        return self.get_page_content(url)
    
    def get_team_statistics_seasons(self, team_id):
        """Get available seasons for team statistics"""
        url = f"{self.BASE_URL}/api/v1/team/{team_id}/team-statistics/seasons"
        return self.get_page_content(url)
    
    def get_team_statistics(self, team_id, ut_id, season_id):
        """Get team statistics for a specific tournament and season"""
        url = f"{self.BASE_URL}/api/v1/team/{team_id}/unique-tournament/{ut_id}/season/{season_id}/statistics/overall"
        return self.get_page_content(url)
    
    def get_event_highlights(self, event_id):
        """Get video highlights for a specific event"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/highlights"
        return self.get_page_content(url)
    
    def get_event_lineups(self, event_id):
        """Get lineups for a specific event"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/lineups"
        return self.get_page_content(url)
    
    def get_tournament_standings(self, tournament_id, season_id):
        """Get standings for a specific tournament and season"""
        url = f"{self.BASE_URL}/api/v1/tournament/{tournament_id}/season/{season_id}/standings/total"
        return self.get_page_content(url)
    
    def get_event_comments(self, event_id):
        """Get comments for a specific event"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/comments"
        return self.get_page_content(url)
    
    def get_tournament_cuptrees(self, ut_id, season_id):
        """Get cup tree structure for a specific tournament and season"""
        url = f"{self.BASE_URL}/api/v1/unique-tournament/{ut_id}/season/{season_id}/cuptrees"
        return self.get_page_content(url)
    
    def get_event_data(self, event_id):
        """Get core event data"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}"
        return self.get_page_content(url)
    
    def get_team_streaks_betting_odds(self, event_id, provider_id):
        """Get team streaks for betting odds"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/team-streaks/betting-odds/{provider_id}"
        return self.get_page_content(url)
    
    def get_event_featured_odds(self, event_id, provider_id):
        """Get featured odds for a specific event and provider"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/odds/{provider_id}/featured"
        return self.get_page_content(url)
    
    def get_event_all_odds(self, event_id, provider_id):
        """Get all odds for a specific event and provider"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/odds/{provider_id}/all"
        return self.get_page_content(url)
    
    def get_event_winning_odds(self, event_id, provider_id):
        """Get winning odds for a specific event and provider"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/provider/{provider_id}/winning-odds"
        return self.get_page_content(url)
    
    def get_event_graph(self, event_id):
        """Get graph data for a specific event"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/graph"
        return self.get_page_content(url)
    
    def get_newly_added_events(self):
        """Get newly added events"""
        url = f"{self.BASE_URL}/api/v1/event/newly-added-events"
        return self.get_page_content(url)
    
    def get_odds_providers(self, country_code):
        """Get odds providers for a specific country"""
        url = f"{self.BASE_URL}/api/v1/odds/providers/{country_code}/web"
        return self.get_page_content(url)
    
    def get_branding_providers(self, country_code):
        """Get branding data for odds providers in a specific country"""
        url = f"{self.BASE_URL}/api/v1/branding/providers/{country_code}/web"
        return self.get_page_content(url)
    
    def get_player_attributes(self, player_id):
        """Get attributes for a specific player"""
        url = f"{self.BASE_URL}/api/v1/player/{player_id}/attribute-overviews"
        return self.get_page_content(url)
    
    def get_event_votes(self, event_id):
        """Get votes/polls for a specific event"""
        url = f"{self.BASE_URL}/api/v1/event/{event_id}/votes"
        return self.get_page_content(url)
    
    def get_team_info(self, team_id):
        """Get core information about a specific team"""
        url = f"{self.BASE_URL}/api/v1/team/{team_id}"
        return self.get_page_content(url)
    
    def get_sport_categories(self):
        """Get all available categories for football"""
        url = f"{self.BASE_URL}/api/v1/sport/football/categories/all"
        return self.get_page_content(url)
    
    def get_sport_scheduled_events(self, date):
        """Get scheduled football events for a specific date"""
        url = f"{self.BASE_URL}/api/v1/sport/football/scheduled-events/{date}"
        return self.get_page_content(url)
    
    def get_live_events(self):
        """Get all live football events"""
        url = f"{self.BASE_URL}/api/v1/sport/football/events/live"
        return self.get_page_content(url)
    
    def get_unique_tournament_info(self, ut_id):
        """Get core information about a specific unique tournament"""
        url = f"{self.BASE_URL}/api/v1/unique-tournament/{ut_id}"
        return self.get_page_content(url)
    
    def get_unique_tournament_seasons(self, ut_id):
        """Get all seasons for a specific unique tournament"""
        url = f"{self.BASE_URL}/api/v1/unique-tournament/{ut_id}/seasons"
        return self.get_page_content(url)
    
    def get_tournament_standings_by_type(self, ut_id, season_id, standings_type="total"):
        """Get tournament standings by type (total, home, away)"""
        url = f"{self.BASE_URL}/api/v1/unique-tournament/{ut_id}/season/{season_id}/standings/{standings_type}"
        return self.get_page_content(url)
    
    def get_tournament_events_last(self, ut_id, season_id, offset=0):
        """Get last events from a tournament season"""
        url = f"{self.BASE_URL}/api/v1/unique-tournament/{ut_id}/season/{season_id}/events/last/{offset}"
        return self.get_page_content(url)
    
    def get_tournament_events_next(self, ut_id, season_id, offset=0):
        """Get next events from a tournament season"""
        url = f"{self.BASE_URL}/api/v1/unique-tournament/{ut_id}/season/{season_id}/events/next/{offset}"
        return self.get_page_content(url)
    
    def get_tournament_top_players(self, ut_id, season_id):
        """Get top players for a tournament season"""
        url = f"{self.BASE_URL}/api/v1/unique-tournament/{ut_id}/season/{season_id}/top-players/overall"
        return self.get_page_content(url)
    
    def get_tournament_top_teams(self, ut_id, season_id):
        """Get top teams for a tournament season"""
        url = f"{self.BASE_URL}/api/v1/unique-tournament/{ut_id}/season/{season_id}/top-teams/overall"
        return self.get_page_content(url)
    
    def get_tournament_rounds(self, ut_id, season_id):
        """Get rounds for a tournament season"""
        url = f"{self.BASE_URL}/api/v1/unique-tournament/{ut_id}/season/{season_id}/rounds"
        return self.get_page_content(url)
    
    def get_tournament_events_by_round(self, ut_id, season_id, round_number):
        """Get events for a specific round in a tournament season"""
        url = f"{self.BASE_URL}/api/v1/unique-tournament/{ut_id}/season/{season_id}/events/round/{round_number}"
        return self.get_page_content(url)


if __name__ == "__main__":
    with SofascoreClient() as client:
        # Example usage:
        # Get football categories
        try:
            categories = client.get_sport_categories()
            print("Categories:", categories)
            # Save as JSON with default name
            categories.json()
            # Save as CSV with default name
            categories.csv()
            # Save as JSON with custom path
            categories.json(path="downloads/data.json")
            # Save as CSV with custom path
            categories.csv(path="downloads/data.csv")
        except Exception as e:
            print(f"Error fetching categories: {e}")