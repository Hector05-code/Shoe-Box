from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd
import io
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, timedelta
from typing import List
from datetime import datetime
from modelos.variante import Variante as VarianteModel
from modelos.producto import Producto as ProductoModel
from modelos.venta import Venta as VentaModel
from modelos.detalle_venta import DetalleVenta as DetalleVentaModel
from modelos.help_categoria import Categoria as CategoriaModel
from schemas.reporte import AlertaStockRead, ReporteVentasRead, TopCategoriaRead
from schemas.empleado import EmpleadoRead
from utilidades.login import get_db, get_usuario_actual

endpoint = APIRouter(prefix="/reportes", tags=["Reportes Gerenciales"])

# REPORTE STOCK BAJO
@endpoint.get("/stock-bajo", response_model=List[AlertaStockRead])
def reporte_stock_bajo(
    db: Session = Depends(get_db),
    _: EmpleadoRead = Depends(get_usuario_actual)
):
    resultados = db.query(VarianteModel, ProductoModel)\
        .join(ProductoModel, VarianteModel.id_producto == ProductoModel.id_producto)\
        .filter(VarianteModel.stock_actual <= VarianteModel.stock_minimo)\
        .filter(VarianteModel.estatus == True)\
        .all()
    
    reporte = []
    for variante, producto in resultados:
        detalle_variante = f"{variante.color_rel.nombre if variante.color_rel else 'N/A'} - {variante.talla_rel.nombre if variante.talla_rel else 'N/A'}"
        
        reporte.append({
            "producto": producto.nombre,
            "variante": detalle_variante,
            "barcode": variante.barcode,
            "stock_actual": variante.stock_actual,
            "stock_minimo": variante.stock_minimo
        })
        
    return reporte


# REPORTE DE VENTAS POR RANGO
@endpoint.get("/ventas", response_model=ReporteVentasRead)
def reporte_ventas_financiero(
    rango: str = Query("hoy", enum=["hoy", "semana", "quincena", "mes"]),
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):

    if usuario_actual.funcion.value != "GERENTE":
        raise HTTPException(status_code=403, detail="Acceso denegado a reportes financieros.")

    fecha_fin = date.today()
    fecha_inicio = date.today()

    if rango == "hoy":
        fecha_inicio = date.today()
    elif rango == "semana":
        fecha_inicio = fecha_fin - timedelta(days=7)
    elif rango == "quincena":
        fecha_inicio = fecha_fin - timedelta(days=15)
    elif rango == "mes":
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    resultado = db.query(
        func.count(VentaModel.id_venta),
        func.sum(VentaModel.total_venta_usd),
        func.sum(VentaModel.total_venta_bolivares)
    ).filter(
        func.date(VentaModel.fecha) >= fecha_inicio,
        func.date(VentaModel.fecha) <= fecha_fin
    ).first()

    cantidad, total_usd, total_bs = resultado
    
    return {
        "rango_fecha": f"Desde {fecha_inicio} hasta {fecha_fin}",
        "cantidad_ventas": cantidad or 0,
        "total_facturado_usd": total_usd or 0.0,
        "total_facturado_bs": total_bs or 0.0,
    }


# REPORTE DE CATEGORÍAS MÁS VENDIDAS
@endpoint.get("/top-categorias", response_model=List[TopCategoriaRead])
def reporte_top_categorias(
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    
    if usuario_actual.funcion.value != "GERENTE":
        raise HTTPException(status_code=403, detail="Acceso denegado.")

    resultados = db.query(
        CategoriaModel.nombre,
        func.sum(DetalleVentaModel.cantidad).label("total_unidades"),
        func.sum(DetalleVentaModel.precio_unitario_usd_snapshot).label("total_dinero")
    ).select_from(CategoriaModel)\
     .join(ProductoModel, CategoriaModel.id_categoria == ProductoModel.id_categoria)\
     .join(VarianteModel, ProductoModel.id_producto == VarianteModel.id_producto)\
     .join(DetalleVentaModel, VarianteModel.id_variante == DetalleVentaModel.id_variante)\
     .group_by(CategoriaModel.id_categoria)\
     .order_by(desc("total_unidades"))\
     .limit(5)\
     .all()

    data = []
    for nombre, unidades, dinero in resultados:
        data.append({
            "categoria": nombre,
            "unidades_vendidas": unidades or 0,
            "dinero_generado_usd": dinero or 0.0
        })
        
    return data

@endpoint.get("/exportar/inventario-excel")
def exportar_inventario_excel(
    db: Session = Depends(get_db),
    _: EmpleadoRead = Depends(get_usuario_actual)
):
    variantes = db.query(VarianteModel).filter(VarianteModel.estatus == True).all()

    data_para_excel = []
    
    for v in variantes:
        data_para_excel.append({
            "Barcode": v.barcode,
            "Marca": v.producto_rel.marca_rel.nombre if v.producto_rel.marca_rel else "N/A",
            "Producto": v.producto_rel.nombre,
            "Color": v.color_rel.nombre,
            "Talla": v.talla_rel.nombre,
            "Stock Actual": v.stock_actual,
            "Stock Mínimo": v.stock_minimo,
            "Costo (REF)": v.costo_usd_esp if v.costo_usd_esp else v.producto_rel.costo_usd,
            "Precio Venta (REF)": v.precio_venta_usd_esp if v.precio_venta_usd_esp else v.producto_rel.precio_venta_usd
        })
    
    df = pd.DataFrame(data_para_excel)

    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventario')
    
    output.seek(0)

    fecha_hoy = datetime.now().strftime("%d - %m - %Y")
    headers = {
        "Content-Disposition": f'attachment; filename="reporte_inventario {fecha_hoy}.xlsx"'
    }
    
    return StreamingResponse(
        output, 
        headers=headers, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )