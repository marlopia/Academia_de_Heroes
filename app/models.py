import random
from typing import cast

from django.db import models
from django.core.exceptions import ValidationError


class Personaje(models.Model):
    vida_max_base: int = 100

    nombre = models.CharField(max_length=100)

    nivel = models.PositiveIntegerField()

    vida = models.PositiveIntegerField()

    vida_max = models.PositiveIntegerField(default=vida_max_base)

    def clean(self):
        """
        Valida que el objeto sea correcto antes de guardarlo en memoria

        Raises:
            ValidationError: Si nivel o vida_max son menores a 1 o vida menor a 0
        """
        if self.nivel < 1:
            raise ValidationError("El nivel tiene que ser mayor o igual a 1")

        if self.vida_max < 1:
            raise ValidationError("La vida máxima tiene que ser mayor o igual a 1")

        if self.vida < 0:
            raise ValidationError("La vida tiene que ser mayor o igual a 0")

        if self.vida > self.vida_max:
            self.vida = self.vida_max

    def save(self, *args, **kwargs):
        """
        Guarda el objeto en memoria tras validarlo
        """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} (Nivel {self.nivel}) - Vida: {self.vida}/{self.vida_max}"

    def esta_vivo(self) -> bool:
        """
        Comprueba que el valor de la vida del personaje sea mayor que 0

        Returns:
            bool: True si el personaje tiene más de 0 de vida
        """
        return self.vida > 0

    def subir_nivel(self):
        """Sube de nivel al personaje, dándole 10 de vida máxima y curándole esa cantidad"""
        self.nivel += 1
        self.vida_max += 10
        self.vida += 10
        self.save()

    def recibir_danio(self, cantidad: int):
        """
        Resta a la vida del personaje la cantidad de daño, pero la vida no baja de 0

        Args:
            cantidad (int): Cantidad de daño a realizar

        Raises:
            ValueError: Si cantidad es menor a 0
        """
        if cantidad < 0:
            raise ValueError("El daño no puede ser negativo")

        self.vida = max(0, self.vida - cantidad)
        self.save()

    def curar(self, cantidad: int):
        """
        Suma a la vida del persona la cantidad de curación, pero la vida no aumenta del máximo

        Args:
            cantidad (int): Cantidad a curar

        Raises:
            ValueError: Si la cantidad a curar es menor a 0
        """
        if cantidad < 0:
            raise ValueError("La curación no puede ser negativa")

        self.vida = min(self.vida_max, self.vida + cantidad)
        self.save()

    def ataque(self):
        """
        Devuelve el daño de un ataque del personaje

        Returns:
            int: 10 * nivel del personaje
        """
        return 10 * self.nivel

    def to_dict(self):
        """
        Devuelve el objeto en formato de diccionario

        Returns:
            dict: El objeto en diccionario
        """
        return {
            "id": self.pk,
            "nombre": self.nombre,
            "nivel": self.nivel,
            "vida": self.vida,
            "vida_max": self.vida_max,
        }


class Guerrero(Personaje):
    armadura = models.PositiveIntegerField(default=0)

    def clean(self):
        super().clean()
        if self.armadura < 0:
            raise ValidationError("La armadura tiene que ser mayor o igual a 0")

    def __str__(self) -> str:
        return f"({self.__class__.__name__}) {super().__str__()} (Armadura: {self.armadura})"

    def recibir_danio(self, cantidad: int) -> None:
        """
        Resta a la vida del personaje la cantidad de daño, pero la vida no baja de 0
        La armadura se resta al daño sufrido.

        Args:
            cantidad (int): Cantidad de daño a realizar

        Raises:
            ValueError: Si cantidad es menor a 0
        """
        if cantidad >= 0:
            if self.vida - (cantidad - self.armadura) >= 0:
                self.vida = self.vida - (cantidad - self.armadura)
            else:
                self.vida = 0
        else:
            raise ValueError("La cantidad de daño realizado no puede ser menor a 0")

    def to_dict(self) -> dict:
        """
        Devuelve el objeto en formato de diccionario

        Returns:
            dict: El objeto en diccionario
        """
        base = super().to_dict()
        base["tipo"] = self.__class__.__name__
        base["armadura"] = self.armadura

        return base


class Mago(Personaje):

    mana = models.PositiveIntegerField(default=0)

    def clean(self):
        super().clean()
        if self.mana < 0:
            raise ValidationError("El maná tiene que ser mayor o igual a 0")

    def __str__(self) -> str:
        return f"({self.__class__.__name__}) {super().__str__()} (Mana:{self.mana})"

    def ataque_especial(self) -> int:
        """
        Si tiene mana realiza un ataque doble, sino realiza 0 de daño

        Returns:
            int: 10 * nivel * 2 si mana >= 10 sino 0
        """
        if self.mana >= 10:
            self.mana = self.mana - 10
            return 10 * self.nivel * 2
        else:
            return 0

    def to_dict(self) -> dict:
        """
        Devuelve el objeto en formato de diccionario

        Returns:
            dict: El objeto en diccionario
        """
        base = super().to_dict()
        base["tipo"] = self.__class__.__name__
        base["mana"] = self.mana

        return base


class Arquero(Personaje):

    precision = models.PositiveIntegerField(default=0)

    def clean(self):
        super().clean()
        if self.precision < 0 or self.precision > 100:
            raise ValidationError("La precisión tiene que ser eentre 0 y 100")

    def __str__(self) -> str:
        return f"({self.__class__.__name__}) {super().__str__()} (Precision: {self.precision})"

    def ataque(self) -> int:
        if self.precision >= random.randint(0, 100):
            return super().ataque()
        else:
            return 0

    def to_dict(self) -> dict:
        """
        Devuelve el objeto en formato de diccionario

        Returns:
            dict: El objeto en diccionario
        """
        base = super().to_dict()
        base["tipo"] = self.__class__.__name__
        base["precision"] = self.precision

        return base


def simular_turno(p1: Personaje, p2: Personaje) -> int:
    """
    Simula un turno de Ataque/Defensa entre dos Personajes

    Args:
        p1 (Personaje): Personaje atacante
        p2 (Personaje): Personaje defensor
    Returns:
        int: El daño de p1.ataque - p2.defensa
    """
    if p1.__class__.__name__ == "Mago":

        p1 = cast(Mago, p1)
        if p1.mana >= 10:
            danio = p1.ataque_especial()
        else:
            danio = p1.ataque()
    else:
        danio = p1.ataque()
    print(f"{p1.nombre} ataca por {danio} de daño")
    p2.recibir_danio(danio)
    print(f"Vida restante de {p2.nombre}: {p2.vida}/{p2.vida_max}")
    return danio
