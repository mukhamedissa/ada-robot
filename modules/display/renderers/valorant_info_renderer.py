import pygame
import os

class ValorantInfoRenderer:
    def __init__(self, screen, project_root):
        self.screen = screen
        self.project_root = project_root

    def render(self, valorant_info):
        account_info = valorant_info.get('account_info', {})
        rank = account_info.get('rank', 'Unknown')
        rr = account_info.get('rr', 0)
        rank_icon_path = valorant_info.get('rank_icon', '')

        screen_width, screen_height = self.screen.get_size()

        if rank_icon_path:
            full_path = os.path.join(self.project_root, rank_icon_path)
            if os.path.exists(full_path):
                try:
                    rank_icon = pygame.image.load(full_path)
                    scaled_icon = pygame.transform.scale(rank_icon, (156, 156))
                    icon_x = (screen_width - 156) // 2
                    icon_y = 10
                    self.screen.blit(scaled_icon, (icon_x, icon_y))
                except Exception as e:
                    print(f"Failed to load rank icon {full_path}: {e}")
            else:
                print(f"Rank icon not found: {full_path}")

        font_large = pygame.font.SysFont(None, 36)
        rank_surface = font_large.render(f"{rank}", True, (255, 255, 255))
        rr_surface = font_large.render(f"{rr} RR", True, (255, 255, 255))

        bottom_margin = 10
        total_text_height = rank_surface.get_height() + rr_surface.get_height() + 10

        rank_x = (screen_width - rank_surface.get_width()) // 2
        rank_y = screen_height - bottom_margin - total_text_height
        rr_x = (screen_width - rr_surface.get_width()) // 2
        rr_y = rank_y + rank_surface.get_height() + 10

        self.screen.blit(rank_surface, (rank_x, rank_y))
        self.screen.blit(rr_surface, (rr_x, rr_y))
