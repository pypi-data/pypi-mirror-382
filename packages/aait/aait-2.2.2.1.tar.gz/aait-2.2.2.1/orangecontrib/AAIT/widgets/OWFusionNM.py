import os
import sys
from typing import Optional, Sequence

import Orange
import Orange.data
from Orange.widgets import widget
from Orange.widgets.settings import Setting
from Orange.widgets.utils.signals import Input, Output

from AnyQt.QtWidgets import (
    QApplication,
    QWidget,
    QComboBox,
    QSizePolicy,
)

# Importations conditionnelles pour refléter l'environnement Orange add-on
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic  # noqa: F401
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import (
        apply_modification_from_python_file,
    )
else:
    from orangecontrib.AAIT.utils.import_uic import uic  # type: ignore  # noqa: F401
    from orangecontrib.AAIT.utils.initialize_from_ini import (  # type: ignore
        apply_modification_from_python_file,
    )



def _var_names(table: Optional[Orange.data.Table]) -> list[str]:
    """Retourne les noms de variables d'une Table Orange.

    Inclut attributs, variables de classe et métadonnées; supprime les doublons
    en conservant l'ordre.
    """
    if table is None:
        return []
    dom = table.domain
    names: list[str] = [v.name for v in list(dom.attributes) + list(dom.class_vars)]
    names += [v.name for v in dom.metas]
    seen = set()
    uniq: list[str] = []
    for n in names:
        if n not in seen:
            uniq.append(n)
            seen.add(n)
    return uniq


@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWFusionNN(widget.OWWidget):
    """Fusion NxM avec NumPy et gestion des non-appareillés.

    - Clé unique sélectionnée pour chaque table
    - Fusion réalisée sans `pd.merge`, en NumPy/dicts
    - Ordre des lignes: matches (NxM), puis A seuls, puis B seuls
    - Colonnes manquantes complétées avec `None`
    - Préservation des variables/types Orange lorsque possible
    """

    name = "Fusion NxM"
    description = "Fusionne deux Tables sur une clé; ajoute les non-appariées"
    category = "AAIT - TOOLBOX"
    icon = "icons/owfusion_nm.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owfusion_nm.png"
    priority = 1095

    want_main_area = True
    want_control_area = False

    # Paramètres persistés
    key1_a: Optional[str] = Setting(None)
    key1_b: Optional[str] = Setting(None)

    class Inputs:
        data_a = Input("Table 1", Orange.data.Table)
        data_b = Input("Table 2", Orange.data.Table)

    class Outputs:
        data = Output("Data", Orange.data.Table)

    def __init__(self) -> None:
        super().__init__()

        self._data_a: Optional[Orange.data.Table] = None
        self._data_b: Optional[Orange.data.Table] = None

        # Charger UI designer si présent, sinon UI minimale
        self.gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owfusion_nm.ui")
        self.form: QWidget = uic.loadUi(self.gui)
        self.mainArea.layout().addWidget(self.form)
        self.form.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cb_key1_a: QComboBox = getattr(self.form, "cb_key1_a")
        self.cb_key1_b: QComboBox = getattr(self.form, "cb_key1_b")
        self.cb_key1_a.currentIndexChanged.connect(self._apply_if_ready)
        self.cb_key1_b.currentIndexChanged.connect(self._apply_if_ready)


        

    class Error(widget.OWWidget.Error):
        no_keys = widget.Msg("Sélectionnez une clé pour A et B.")
        fusion = widget.Msg("Erreur de fusion: {}")

    # ---------- Entrées ----------
    @Inputs.data_a
    def set_data_a(self, data: Optional[Orange.data.Table]):
        self._data_a = data
        self._populate_combos()
        self._maybe_autoselect_keys()
        self._apply_if_ready()

    @Inputs.data_b
    def set_data_b(self, data: Optional[Orange.data.Table]):
        self._data_b = data
        self._populate_combos()
        self._maybe_autoselect_keys()
        self._apply_if_ready()

    # ---------- Aide UI ----------
    def _populate_combos(self) -> None:
        names_a = _var_names(self._data_a)
        names_b = _var_names(self._data_b)

        def fill(cb: QComboBox, items: Sequence[str], target_value: Optional[str]):
            current = cb.currentText()
            cb.blockSignals(True)
            cb.clear()
            cb.addItems(items)
            if target_value and target_value in items:
                cb.setCurrentText(target_value)
            elif current in items:
                cb.setCurrentText(current)
            cb.blockSignals(False)

        if hasattr(self, "cb_key1_a"):
            fill(self.cb_key1_a, names_a, self.key1_a)
        if hasattr(self, "cb_key1_b"):
            fill(self.cb_key1_b, names_b, self.key1_b)

    def _maybe_autoselect_keys(self) -> None:
        if not hasattr(self, "cb_key1_a") or not hasattr(self, "cb_key1_b"):
            return
        if not self.key1_a and self.cb_key1_a.count() > 0:
            self.key1_a = self.cb_key1_a.itemText(0)
            self.cb_key1_a.setCurrentIndex(0)
        if not self.key1_b and self.cb_key1_b.count() > 0:
            self.key1_b = self.cb_key1_b.itemText(0)
            self.cb_key1_b.setCurrentIndex(0)

    def _apply_if_ready(self) -> None:
        if self._data_a is None or self._data_b is None:
            return
        if not hasattr(self, "cb_key1_a") or not hasattr(self, "cb_key1_b"):
            return
        if self.cb_key1_a.count() == 0 or self.cb_key1_b.count() == 0:
            return
        if self.cb_key1_a.currentIndex() < 0 or self.cb_key1_b.currentIndex() < 0:
            return
        self._apply()

    # ---------- Appliquer la fusion ----------
    def _apply(self) -> None:
        a = self._data_a
        b = self._data_b
        if a is None or b is None:
            self.Outputs.data.send(None)
            return

        # Lire les clés sélectionnées
        self.key1_a = self.cb_key1_a.currentText() or None
        self.key1_b = self.cb_key1_b.currentText() or None

        self.Error.no_keys.clear()
        self.Error.fusion.clear()

        if not (self.key1_a and self.key1_b):
            self.Error.no_keys()
            self.Outputs.data.send(None)
            return

        try:
            import numpy as np

            key_a = self.key1_a  # type: ignore[assignment]
            key_b = self.key1_b  # type: ignore[assignment]

            # Récupérer variables et index pour A
            attrs_a = list(a.domain.attributes)
            class_a = list(a.domain.class_vars)
            metas_a = list(a.domain.metas)
            ai_attr = {v.name: i for i, v in enumerate(attrs_a)}
            ai_class = {v.name: i for i, v in enumerate(class_a)}
            ai_meta = {v.name: i for i, v in enumerate(metas_a)}

            # Récupérer variables et index pour B
            attrs_b = list(b.domain.attributes)
            class_b = list(b.domain.class_vars)
            metas_b = list(b.domain.metas)
            bi_attr = {v.name: i for i, v in enumerate(attrs_b)}
            bi_class = {v.name: i for i, v in enumerate(class_b)}
            bi_meta = {v.name: i for i, v in enumerate(metas_b)}

            names_a = [v.name for v in attrs_a + class_a + metas_a]
            names_b = [v.name for v in attrs_b + class_b + metas_b]
            overlap = set(names_a).intersection(names_b)
            same_key_name = key_a == key_b

            # Construire liste de variables de sortie et mapping de colonnes
            out_attrs: list[Orange.data.Variable] = []
            out_classes: list[Orange.data.Variable] = []
            out_metas: list[Orange.data.Variable] = []

            # Pour chaque position de sortie, mémoriser (side, role, src_idx)
            src_attrs: list[tuple[str, str, int]] = []
            src_classes: list[tuple[str, str, int]] = []
            src_metas: list[tuple[str, str, int]] = []

            # Ajout depuis A
            for v in attrs_a:
                name = v.name
                if name in overlap and not (same_key_name and name == key_a):
                    vv = v.copy(compute_value=None)
                    vv.name = f"{name}_A"
                else:
                    vv = v
                out_attrs.append(vv)
                src_attrs.append(("A", "attr", ai_attr[name]))

            for v in class_a:
                name = v.name
                if name in overlap and not (same_key_name and name == key_a):
                    vv = v.copy(compute_value=None)
                    vv.name = f"{name}_A"
                else:
                    vv = v
                out_classes.append(vv)
                src_classes.append(("A", "class", ai_class[name]))

            for v in metas_a:
                name = v.name
                if name in overlap and not (same_key_name and name == key_a):
                    vv = v.copy(compute_value=None)
                    vv.name = f"{name}_A"
                else:
                    vv = v
                out_metas.append(vv)
                src_metas.append(("A", "meta", ai_meta[name]))

            # Ajout depuis B
            for v in attrs_b:
                name = v.name
                if same_key_name and name == key_b:
                    continue  # éviter la duplication de la clé si même nom
                if name in overlap:
                    vv = v.copy(compute_value=None)
                    vv.name = f"{name}_B"
                else:
                    vv = v
                out_attrs.append(vv)
                src_attrs.append(("B", "attr", bi_attr[name]))

            for v in class_b:
                name = v.name
                if same_key_name and name == key_b:
                    continue
                if name in overlap:
                    vv = v.copy(compute_value=None)
                    vv.name = f"{name}_B"
                else:
                    vv = v
                out_classes.append(vv)
                src_classes.append(("B", "class", bi_class[name]))

            for v in metas_b:
                name = v.name
                if same_key_name and name == key_b:
                    continue
                if name in overlap:
                    vv = v.copy(compute_value=None)
                    vv.name = f"{name}_B"
                else:
                    vv = v
                out_metas.append(vv)
                src_metas.append(("B", "meta", bi_meta[name]))

            # Extraction des colonnes de clés
            def col_values(table: Orange.data.Table, name: str):
                if name in {v.name for v in table.domain.attributes}:
                    idx = {v.name: i for i, v in enumerate(table.domain.attributes)}[name]
                    return table.X[:, idx]
                elif name in {v.name for v in table.domain.class_vars}:
                    idx = {v.name: i for i, v in enumerate(table.domain.class_vars)}[name]
                    y = table.Y
                    if y.size == 0:
                        return np.array([])
                    if y.ndim == 1:
                        # single class var
                        if idx != 0:
                            return np.array([np.nan] * len(table))
                        return y
                    return y[:, idx]
                elif name in {v.name for v in table.domain.metas}:
                    idx = {v.name: i for i, v in enumerate(table.domain.metas)}[name]
                    return table.metas[:, idx]
                else:
                    return np.array([])

            ka = col_values(a, key_a)
            kb = col_values(b, key_b)

            # Comparaison des clés (None/NaN ne matchent pas)
            def is_nan(x):
                try:
                    return np.isnan(x)
                except Exception:
                    return False

            def is_equal(x, y):
                if x is None or y is None:
                    return False
                if is_nan(x) or is_nan(y):
                    return False
                return x == y

            # Index B: valeur -> indices
            from collections import defaultdict
            idx_b = defaultdict(list)
            kb_list = kb.tolist()
            for j, v in enumerate(kb_list):
                if v is None or is_nan(v):
                    continue
                try:
                    idx_b[v].append(j)
                except Exception:
                    # non-hashable: ignoré ici, on s'appuiera sur fallback
                    pass

            matched_pairs: list[tuple[int, int]] = []
            matched_a = np.zeros(len(ka), dtype=bool)
            matched_b = np.zeros(len(kb), dtype=bool)
            ka_list = ka.tolist()
            for i, va in enumerate(ka_list):
                js = idx_b.get(va)
                if js is None:
                    js = [j for j, vb in enumerate(kb_list) if is_equal(va, vb)]
                if js:
                    for j in js:
                        matched_pairs.append((i, j))
                        matched_a[i] = True
                        matched_b[j] = True

            a_only = [i for i, m in enumerate(matched_a) if not m]
            b_only = [j for j, m in enumerate(matched_b) if not m]

            # Construire Domain de sortie
            out_domain = Orange.data.Domain(out_attrs, out_classes, out_metas)

            # Allouer matrices de sortie
            n_rows = len(matched_pairs) + len(a_only) + len(b_only)
            X_out = np.full((n_rows, len(out_attrs)), np.nan)
            if len(out_classes) == 0:
                Y_out = None
            elif len(out_classes) == 1:
                Y_out = np.full((n_rows,), np.nan)
            else:
                Y_out = np.full((n_rows, len(out_classes)), np.nan)
            M_out = np.full((n_rows, len(out_metas)), None, dtype=object)
            def normalize_meta_value(value):
                if value is None:
                    return None
                if isinstance(value, (float, np.floating)):
                    if np.isnan(value):
                        return None
                try:
                    if value != value:
                        return None
                except Exception:
                    pass
                return value

            # Helpers d'accès aux valeurs source
            def get_class_val(table: Orange.data.Table, row: int, idx: int):
                y = table.Y
                if y.size == 0:
                    return np.nan
                if y.ndim == 1:
                    if idx != 0:
                        return np.nan
                    return y[row]
                return y[row, idx]

            def set_row_from_side(side: str, src_row: int, out_row: int):
                src_table = a if side == "A" else b
                # attributes
                for pos, (s, role, idx) in enumerate(src_attrs):
                    if s != side:
                        continue
                    if role == "attr" and src_table.X.shape[1] > idx:
                        X_out[out_row, pos] = src_table.X[src_row, idx]
                # classes
                for pos, (s, role, idx) in enumerate(src_classes):
                    if s != side:
                        continue
                    val = get_class_val(src_table, src_row, idx)
                    if len(out_classes) == 1:
                        if pos == 0:
                            Y_out[out_row] = val  # type: ignore[index]
                    else:
                        Y_out[out_row, pos] = val  # type: ignore[index]
                # metas
                for pos, (s, role, idx) in enumerate(src_metas):
                    if s != side:
                        continue
                    if src_table.metas.shape[1] > idx:
                        raw_value = src_table.metas[src_row, idx]
                        M_out[out_row, pos] = normalize_meta_value(raw_value)

            # Remplir lignes: appariées, puis A-only, puis B-only
            r = 0
            for i, j in matched_pairs:
                set_row_from_side("A", i, r)
                set_row_from_side("B", j, r)
                r += 1
            for i in a_only:
                set_row_from_side("A", i, r)
                r += 1
            for j in b_only:
                set_row_from_side("B", j, r)
                r += 1

            out = Orange.data.Table.from_numpy(out_domain, X_out, Y_out, M_out)
            out.name = (a.name or "A") + " outer(numpy) " + (b.name or "B")
            self.Outputs.data.send(out)
        except Exception as ex:  # pragma: no cover
            self.Error.fusion(str(ex))
            self.Outputs.data.send(None)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWFusionNN()
    w.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()
