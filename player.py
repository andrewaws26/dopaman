
class Player:
    # ...existing code...

    def recharge_dopamine(self, amount):
        """Recharge dopamine when MJF is nearby"""
        self.dopamine = min(self.max_dopamine, self.dopamine + amount)
        # Visual feedback for recharge
        if hasattr(self, 'recharge_particles'):
            self.recharge_particles.append([
                self.rect.centerx,
                self.rect.centery,
                0  # Particle lifetime
            ])